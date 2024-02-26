from pathlib import Path
import os

import click


def mapping_numbered(directory: Path, regex: str, f: bool) -> None:
    files = list(directory.glob(regex))
    files.sort()
    mapping = []
    for i, file in enumerate(files):
        mapping.append([file.name.split('.')[0], f'{i + 1:04d}'])
        if not f:
            os.rename(file, f'{i + 1:04d}{"".join(file.suffixes)}')
    with open(directory.joinpath('mapping.txt'), 'w') as f:
        for item in mapping:
            f.write(f'{item[0]} -> {item[1]}\n')


def mapping_original(directory: Path, mapping: Path) -> None:
    with open(mapping, 'r') as f:
        mapping = f.readlines()
    for line in mapping:
        original, numbered = line.split(' -> ')
        original = original.strip()
        numbered = numbered.strip()
        files = list(directory.glob(f'{numbered}.*'))
        for file in files:
            os.rename(file, directory.joinpath(f'{original}{"".join(file.suffixes)}'))


@click.command('mapping', short_help='Rename files either numbered or original names with mapping file.')
@click.help_option('--help', '-h')
@click.argument(
    'directory',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.argument(
    'mapping',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=False
)
@click.option(
    '-m', '--mode',
    help='numbered: rename files with numbers, original: rename files with original names.',
    type=click.Choice(['numbered', 'original'], case_sensitive=False),
    required=True
)
@click.option(
    '-r', '--regex',
    help='Input filename regular expression (example: *.orig.png).',
    type=str,
    default='*',
    show_default=True,
    required=False
)
@click.option(
    '-f', '--file',
    help='Outputs only mapping.txt file without rename.',
    is_flag=True,
    type=bool,
    required=False
)
def mapping_cli(directory: str, mapping: str, mode: str, regex: str, file: bool) -> None:
    """
    Rename files either numbered and create mapping file or use mapping file to restore original names.
    
    MAPPING file defaults to DIRECTORY/mapping.txt, only used in ORIGINAL mode.
    """
    match(mode):
        case 'numbered':
            mapping_numbered(directory=Path(directory), regex=regex, f=file)
        case 'original':
            if mapping is None:
                mapping = Path(directory).joinpath('mapping.txt')
            mapping_original(directory=Path(directory), mapping=Path(mapping))
            