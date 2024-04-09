from pathlib import Path
from os import rename as os_rename

import click


def replace(files: list[Path], f: str, t: str = ''):
    with click.progressbar(files, label='Renaming files', show_pos=True, show_eta=True, show_percent=True) as file_list:
        for file in file_list:
            os_rename(file, file.parent.joinpath(file.name.replace(f, t)))


def dots(files: list[Path], f: str = '_', k: int = 1):
    with click.progressbar(files, label='Renaming files', show_pos=True, show_eta=True, show_percent=True) as file_list:
        for file in file_list:
            parts = file.name.split('.')
            k = min(k, len(parts) - 1)
            os_rename(file, file.parent.joinpath(f'{f.join(parts[0:-k])}.{".".join(parts[-k:])}'))


def enum(files: list[Path], o: Path):
    map_list = []
    with click.progressbar(files, label='Renaming files', show_pos=True, show_eta=True, show_percent=True) as file_list:
        for i, file in enumerate(file_list):
            map_list.append((file.name, f'{i + 1:05d}.{".".join(file.name.split(".")[1:])}'))
            os_rename(file, file.parent.joinpath(f'{i + 1:05d}.{".".join(file.name.split(".")[1:])}'))
    with open(o.joinpath('mapping.txt'), 'w') as f:
        for item in map_list:
            f.write(f'{item[0]} -> {item[1]}\n')


def mapping(files: Path, m: Path):
    with open(m, 'r') as f:
        map_list = f.readlines()
    with click.progressbar(map_list, label='Renaming files', show_pos=True, show_eta=True, show_percent=True) as maps:
        for line in maps:
            original, mapped = line.split(' -> ')
            original = original.strip()
            mapped = mapped.strip()
            os_rename(files.joinpath(mapped), files.joinpath(original))


@click.command('rename', short_help='Rename a set of files.')
@click.help_option('--help', '-h')
@click.argument(
    'files',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.option(
    '-p', '--replace', 'option',
    help='Replaces a substring with another string or nothing. '
         'First argument: substring (required). '
         'Second argument: replacement string (default=None).',
    flag_value='rename'
)
@click.option(
    '-d', '--dots', 'option',
    help='Replaces dots with another char. '
         'First argument: replacement char (default=_). '
         'Second argument: suffixes to keep (default=1).',
    flag_value='dots'
)
@click.option(
    '-e', '--enumerate', 'option',
    help='Enumerate files and create mapping file. '
         'First argument: mapping file output path (default=FILES).',
    flag_value='enumerate'
)
@click.option(
    '-m', '--mapping', 'option',
    help='Rename files according to mapping file. '
         'First argument: mapping file path (required).',
    flag_value='mapping'
)
@click.option(
    '-r', '--regex',
    help='Glob Regex for file selection.',
    type=click.STRING,
    default='*',
    show_default=True
)
@click.argument(
    'arguments',
    nargs=-1
)
def rename_cli(files, option: str, regex: str, arguments: tuple):
    """
    Rename a set of files by specified rules.
    """
    fp = sorted(list([f for f in Path(files).glob(regex) if f.is_file()]))
    arg_count = len(arguments)
    match option:
        case 'rename':
            if arg_count < 1:
                click.echo('Wrong number of arguments', err=True)
            elif arg_count == 1:
                replace(fp, f=arguments[0], t='')
            else:
                replace(fp, f=arguments[0], t=arguments[1])
        case 'dots':
            if arg_count < 1:
                dots(fp)
            elif arg_count == 1:
                dots(fp, f=arguments[0])
            else:
                dots(fp, f=arguments[0], k=int(arguments[1]))
        case 'enumerate':
            if arg_count < 1:
                enum(fp, o=Path(files))
            else:
                enum(fp, o=Path(arguments[0]))
        case 'mapping':
            if arg_count < 1:
                click.echo('Wrong number of arguments', err=True)
            else:
                mapping(Path(files), m=Path(arguments[0]))
