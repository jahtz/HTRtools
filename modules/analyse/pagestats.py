import csv
from pathlib import Path

import bs4
import click

from utils import TextRegion


class RegionStats:
    def __init__(self, fp: Path):
        if not fp.exists():
            raise FileNotFoundError(fp.as_posix())
        elif fp.is_file():
            self.files = [fp]
        else:
            self.files = list(Path(fp).glob('*.xml'))
            self.files.sort()

    def run(self, out_fp: Path | None):
        stats = {}
        for file in self.files:
            with open(file, 'r', encoding='utf-8') as f:
                stream = f.read()
                bs = bs4.BeautifulSoup(stream, 'xml')
            regions = []
            for text_region in bs.find_all('TextRegion'):
                if text_region.has_attr('type'):
                    _type = text_region['type']
                elif text_region.has_attr('custom'):
                    _type = text_region['custom'].replace('structure {type:', '').replace(';}', '')
                else:
                    _type = 'missing attribute'
                region = TextRegion(text_region['id'], _type)
                region.set_lines(len(text_region.find_all('TextLine')))
                regions.append(region)
            stats[file.name] = regions
        if out_fp is not None:
            self.stats_to_csv(stats, out_fp.joinpath('stats.csv'))
        else:
            self.stats_to_console(stats)

    @staticmethod
    def stats_to_console(stats: dict):
        region_types = set()
        for page in stats:
            for region in stats[page]:
                region_types.add(region.get_type())
        header = ['page']
        for _type in region_types:
            header.append(_type)
        header.append('total')
        for page in stats:
            line_count = 0
            content = list([0 for x in range(len(header))])
            content[0] = page.replace('.xml', '')
            click.echo(f'{content[0]}:')
            for region in stats[page]:
                content[header.index(region.get_type())] += region.get_lines()
                line_count += region.get_lines()
            content[-1] = line_count
            for i in range(1, len(content)):
                click.echo(f'\t{header[i]}: {content[i]}')

    @staticmethod
    def stats_to_csv(stats: dict, out_fp: Path):
        region_types = set()
        for page in stats:
            for region in stats[page]:
                region_types.add(region.get_type())
        header = ['page']
        for _type in region_types:
            header.append(_type)
        header.append('total')

        with open(out_fp, 'w', encoding='utf') as f:
            stream = csv.writer(f)
            stream.writerow(header)
            for page in stats:
                line_count = 0
                content = list([0 for x in range(len(header))])
                content[0] = page.replace('.xml', '')
                for region in stats[page]:
                    content[header.index(region.get_type())] += region.get_lines()
                    line_count += region.get_lines()
                content[-1] = line_count
                stream.writerow(content)


@click.command('pagestats', short_help='Outputs stats of PageXML files.')
@click.help_option('--help', '-h')
@click.argument(
    'xml_files',
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    required=True
)
@click.argument(
    'output_directory',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=False
)
@click.option(
    '-r', '--regions',
    help='Outputs region count and types.',
    is_flag=True,
    type=bool,
    default=False
)
def pagestats_cli(xml_files: str, output_directory: str | None, regions: bool):
    """
    Outputs stats of one or multiple PageXML files.

    XML_FILES can either be a directory containing multiple .xml files or a single .xml file.

    Creates a stats.csv file in OUTPUT_DIRECTORY or prints stats to console if OUTPUT_DIRECTORY is not specified.
    """
    if regions:
        RegionStats(Path(xml_files)).run(None if output_directory is None else Path(output_directory))
    else:
        click.echo('No option specified. Use --help for more information.', err=True)
