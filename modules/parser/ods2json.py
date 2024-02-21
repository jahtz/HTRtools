from pathlib import Path
import json

import pandas
import click


def ods2json(in_fp: Path, out_fp: Path, prettify: bool, indent: int = 4) -> None:
    json_data = []
    rf = pandas.read_excel(in_fp)
    rules = rf.fillna('').to_dict(orient='split')['data']
    convert_2d_values_to_string(rules)
    for rule in rules:
        json_data.append({'rule': rule, 'type': 'raw'})
    with open(out_fp, 'w', encoding='utf-8') as fp:
        if prettify:
            fp.write('[\n')
            for i, row in enumerate(json_data):
                fp.write(
                    f'{" " * indent}{json.dumps(row, ensure_ascii=False)}{"," if i < len(json_data) - 1 else ""}\n')
            fp.write(']')
        else:
            json.dump(json_data, fp)


def convert_2d_values_to_string(l: list) -> None:
    for i, m in enumerate(l):
        for j, n in enumerate(m):
            l[i][j] = str(l[i][j]).strip()


@click.command('ods2json', short_help='Extracts mapping data from ODS file to PAGETools compatible JSON format.')
@click.help_option('--help', '-h')
@click.argument(
    'input_ods',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True
)
@click.argument(
    'output_json',
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    required=True
)
@click.option(
    '-p', '--disable_prettify',
    help='Disable pretty printing.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-i', '--indent',
    help='Pretty printing indentation. Ignored if -p is set.',
    type=int,
    default=4,
    show_default=True,
    required=False
)
def ods2json_cli(input_ods: str, output_json: str, disable_prettify: bool, indent: int) -> None:
    """
    Extracts mapping data from .ods file to PAGETools compatible json format.

    PAGETools: https://github.com/uniwue-zpd/PAGETools

    OUTPUT_TXT of format '/path/to/file.json'.
    """
    click.echo('Extracting content...', nl=False)
    ods2json(Path(input_ods), Path(output_json), not disable_prettify, indent)
    click.echo(' Done')
