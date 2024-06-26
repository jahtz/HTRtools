import csv
from pathlib import Path

import click


def csv2txt(csv_fp: Path, txt_fp: Path, column: int, skip: bool = False) -> None:
    cells = []
    with open(csv_fp.as_posix(), 'r', encoding='utf-8') as f:
        stream = csv.reader(f, delimiter=',')
        for row in stream:
            if row[column]:
                cells.append(row[column])
            elif not skip:
                cells.append('')

    with open(txt_fp.as_posix(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(cells))


@click.command('csv2txt', short_help='Extracts a column from a CSV file into a TXT file.')
@click.help_option('--help', '-h')
@click.argument(
    'csv_in',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True
)
@click.argument(
    'txt_out',
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    required=True
)
@click.option(
    '-c', '--column',
    help='Column to extract.',
    type=int,
    default=0,
    show_default=True,
    required=False
)
@click.option(
    '-s', '--skip',
    help='Skip empty cells, else insert blank line.',
    is_flag=True,
    type=bool,
    default=False
)
def csv2txt_cli(csv_in: str, txt_out: str, column: int, skip: bool) -> None:
    """
    Extracts a column from a .csv file into a .txt file.

    TXT_OUT of format '/path/to/file.txt'.

    Made for pagesearch script.
    """
    click.echo('Extracting content...', nl=False)
    csv2txt(Path(csv_in), Path(txt_out), column, skip)
    click.echo(' Done')
    