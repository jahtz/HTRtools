from pathlib import Path
import os

import click


def filenamecut(directory: Path, cut_length: int, regex: str) -> None:
    files = list(directory.glob(regex))
    for file in files:
        os.rename(file, directory.joinpath(file.name[cut_length:]))


@click.command('filenamecut', short_help='Cuts first i characters from filenames.')
@click.help_option('--help', '-h')
@click.argument(
    'directory',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.argument(
    'cut_length',
    type=int,
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
def filenamecut_cli(directory: str, cut_length: int, regex: str) -> None:
    """
    Cuts first CUT_LENGTH characters from filenames.
    """
    filenamecut(
        directory=Path(directory),
        cut_length=cut_length,
        regex=regex
    )
    