import csv
import os
import bs4
import shutil
import configparser
from pathlib import Path
from glob import glob

import click
from lxml import etree

DEFAULT_CONFIG = Path(__file__).parent.parent.parent.joinpath('config', 'pagesearch.cfg')
CSV_HEADER = ['search', 'out_file', 'line', 'text', 'original_file']
CSV_FILE = 'results.csv'


class PageSearch:
    def __init__(
            self,
            input_dir: Path,
            output_dir: Path = None,
            recursive: bool = True,
            config: Path = DEFAULT_CONFIG
    ) -> None:
        """
        Loads all .xml files from a folder based on arguments and makes them searchable

        :param input_dir: input directory root path
        :param output_dir: output directory (will be created if not existent)
        :param recursive: search all folders recursively
        :param config: change default config file path
        """
        self.__input_dir: Path = input_dir
        self.__output_dir: Path = output_dir
        self.__recursive: bool = recursive
        self.__config: Path = config

        self.__xml_config = ''
        self.__copy_config = []
        self.__xml_update = ''
        self.__ex_files = []
        self.__ex_folders = []
        self.__load_config()

        self.files: list[Path] = []
        self.__load_files()

    def __load_config(self) -> None:
        """
        Loads config file with argparse

        :return: None
        """
        cfg = configparser.ConfigParser(converters={
            'list': lambda x: [i.strip() for i in x.splitlines() if i != ''],
            'map': lambda x: [i.replace(' ', '').split('>') for i in x.splitlines() if i != ''],
        })
        cfg.read(DEFAULT_CONFIG.as_posix())
        self.__xml_config = cfg.get('EXTENSIONS', 'xml')
        self.__copy_config = cfg.getmap('EXTENSIONS', 'copy')
        self.__xml_update = cfg.get('EXTENSIONS', 'xml_update')
        self.__ex_files = cfg.getlist('EXCLUDED', 'files')
        self.__ex_folders = cfg.getlist('EXCLUDED', 'folders')

    def __load_files(self) -> None:
        """
        loads all .xml paths

        :return: None
        """
        self.files = glob(self.__input_dir.joinpath('**', f'*{self.__xml_config}').as_posix(),
                          recursive=self.__recursive)
        self.files = list(filter(lambda p: Path(p).name not in self.__ex_files, self.files))  # remove excluded files
        self.files = list(filter(lambda p: not any(
            folder in Path(p).relative_to(self.__input_dir).as_posix() for folder in self.__ex_folders),
                                 self.files))  # remove excluded folders
        self.files.sort()

    @staticmethod
    def __parse_search(fp: Path) -> list[str]:
        """
        parse search file and returns list of char sequences

        :param fp: path to file
        :return: list of file content
        """
        with open(fp.as_posix(), 'r', encoding='utf-8') as f:
            data = f.readlines()
        return [x.strip() for x in data if x.strip() != '' and not x.startswith('#')]

    @staticmethod
    def __get_line_text(text_line: bs4.PageElement) -> str:
        """
        extracts text from a TextLine elements, returns empty string if nothing found

        :param text_line:
        :return:
        """
        equiv = text_line.find_all('TextEquiv', recursive=False)
        if not equiv:
            return ''
        for index_line in equiv:
            if 'index' not in index_line:
                line = index_line.find('Unicode')
                if line is None:
                    return ''
                return line.text
            else:
                if index_line['index'] == 0:
                    line = index_line.find('Unicode')
                    if line is None:
                        return ''
                    return line.text
        return ''

    @staticmethod
    def __print_results(results: dict) -> None:
        """
        Prints results of search in readable format

        :param results: results dictionary from search method
        :return: None
        """
        for key, val in results.items():
            click.echo(key)
            for hits in val:
                click.echo(f'\tFound {hits["search"]} in line {hits["line"]}: "{hits["text"]}"')

    def __write_csv(self, content: list[list]) -> Path:
        """
        Writes a nested list to a csv file, name specified in global variables

        :param content: nested list of data
        :return: path to csv file
        """
        fp = Path(self.__output_dir.joinpath(CSV_FILE))
        with open(fp.as_posix(), 'w', encoding='utf-8', newline='') as f:
            stream = csv.writer(f)
            stream.writerow(CSV_HEADER)
            stream.writerows(content)
        return fp

    @staticmethod
    def __fix_xml(xml_path: Path, filename: str) -> None:
        """
        Tries to change imageFilename in pageXML file

        :param xml_path: path to xml file
        :param filename: new filename
        :return: None
        """
        root = etree.parse(xml_path).getroot()
        if root is None:
            return
        try:
            page = root.find(".//{*}Page")
            page.set('imageFilename', filename)
            with open(xml_path, "w", encoding='utf-8') as outfile:
                outfile.write(etree.tostring(root, encoding="unicode", pretty_print=True))
        except Exception as e:
            click.echo(e, err=True)

    def __copy_results(self, results: dict) -> Path:
        """
        Copy and rename files specified in config.cfg to output folder and creates results.csv in output folder

        :param results: results dictionary from search method
        :return: path to results.csv file
        """
        if not self.__output_dir.exists():
            os.mkdir(self.__output_dir)

        csv_content = []
        fc = 1  # file counter
        for path, hits in results.items():
            orig_xml_path = Path(path)
            orig_name = orig_xml_path.name.replace(self.__xml_config, '')  # removes xml file extension
            for ext_index in range(len(self.__copy_config)):
                # generate paths and filenames
                orig_path = orig_xml_path.parent.joinpath(f'{orig_name}{self.__copy_config[ext_index][0]}')
                new_path = self.__output_dir.joinpath(f'{fc:05d}{self.__copy_config[ext_index][1]}')
                if orig_path.exists():
                    shutil.copy(orig_path, new_path)
                    # update xml if needed
                    if self.__copy_config[ext_index][0] == self.__xml_config and self.__xml_update:
                        self.__fix_xml(new_path, f'{fc:05d}{self.__xml_update}')
                else:
                    click.echo(f'FileNotFound (skip): {orig_path.as_posix()} > {new_path.as_posix()}')
            # prepare data for csv file
            for hit in hits:
                csv_content.append([
                    hit['search'],
                    f'{fc:05d}',
                    hit['line'],
                    # hit['region'],
                    hit['text'],
                    orig_xml_path.parent.relative_to(self.__input_dir).joinpath(orig_name).as_posix()
                ])
            fc += 1
        return self.__write_csv(csv_content)

    def search(self, search_fp: Path, console: bool = False) -> None:
        """
        searches for char sequences from search text file and outputs results in csv file in output folder.
        copies affected files to output folder (numerated file names) if specified in config.cfg.
        Outputs results only on console if console set to True.

        :param search_fp: path to search text file
        :param console: output results only on console
        :return: None
        """
        search = self.__parse_search(search_fp)
        if not search:
            click.echo('Search empty!')
            return

        if not console and not self.__output_dir:
            click.echo('No output directory set!')
            return

        result: dict = {}  # key: file path, value: list of found data
        for fp in self.files:
            with open(fp, 'r', encoding='utf-8') as f:
                stream = f.read()
                bs = bs4.BeautifulSoup(stream, 'xml')
            for iter_area in bs.find_all('TextRegion'):
                line_counter = 0  # count lines in file
                for iter_line in iter_area.find_all('TextLine'):
                    # line_id = iter_line['id'].replace('l', '')
                    line_text = self.__get_line_text(iter_line)
                    if line_text == '':  # filter empty lines
                        continue
                    for s in search:
                        # check for any search symbol in line
                        if s in line_text:
                            if fp not in result:
                                result[fp] = []
                            result[fp].append({
                                'line': line_counter,
                                'region': iter_area['id'].replace('r', ''),
                                'text': line_text,
                                'search': s,
                            })
                    line_counter += 1

        if result:
            if console:
                self.__print_results(result)
            else:
                csv_file = self.__copy_results(result)
                click.echo(f'Done! ({csv_file})')
        else:
            click.echo('Nothing found!')
            return


@click.command('pagesearch', short_help='Search for characters in set of PageXML files.')
@click.help_option('--help', '-h')
@click.argument(
    'input_dir',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True,
)
@click.argument(
    'search_file',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
)
@click.option(
    '-c', '--console',
    help='Prints output to console (without file copy).',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-r', '--recursive',
    help='Recursive search in input directory.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-o', '--output',
    help='Target directory for copied images and output results.csv file. Ignored if -c/--console is set.',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=False
)
@click.option(
    '--config',
    help='Use custom config.cfg file.',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    default=DEFAULT_CONFIG,
    show_default=True,
    required=False
)
def pagesearch_cli(input_dir: str, search_file: str, console: bool, recursive: bool, output: str, config: str):
    """
    Search for characters in set of PageXML files.

    Creates a directory with content based on rules specified in './config/pagesearch.cfg'.

    INPUT_DIR should be a directory containing PageXML files and matching images.

    SEARCH_FILE examples can be found in './examples/' folder.
    """
    PageSearch(
        input_dir=Path(input_dir).absolute(),
        output_dir=None if output is None else Path(output).absolute(),
        recursive=recursive,
        config=Path(config).absolute()
    ).search(
        search_fp=Path(search_file).absolute(),
        console=console or (output is None)
    )
