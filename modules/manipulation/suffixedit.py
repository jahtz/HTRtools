from pathlib import Path
import os

import click


def suffixedit(directory: Path, old_suffix: str, new_suffix: str, blacklist: tuple, recursive: bool) -> None:
    fl = [x.absolute() for x in directory.glob(f'{"**/" if recursive else ""}*{old_suffix}')]
    if blacklist:
        fl = list(filter(lambda p: not any(bl in p.name for bl in blacklist), fl))
    fl.sort()
    with click.progressbar(fl, label='Rename file', show_pos=True, item_show_func=lambda x: f'{f"({x.name})" if x is not None else ""}') as files:
        for file in files:
            os.rename(file, file.as_posix().replace(old_suffix, new_suffix))


@click.command('suffixedit', short_help='Edit suffix of multiple files.')
@click.help_option('--help', '-h')
@click.argument(
    'directory',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.argument(
    'old_suffix',
    type=str,
    required=True
)
@click.argument(
    'new_suffix',
    type=str,
    required=True
)
@click.option(
    '-b', '--blacklist',
    help='Blacklist suffixes, multiple items are allowed.',
    type=str,
    multiple=True,
    required=False,
)
@click.option(
    '-r', '--recursive',
    help='Walk through subdirectories recursively.',
    is_flag=True,
    type=bool,
    required=False
)
def suffixedit_cli(directory: str, old_suffix: str, new_suffix: str, blacklist: tuple, recursive: bool) -> None:
    suffixedit(
        directory=Path(directory),
        old_suffix=old_suffix,
        new_suffix=new_suffix,
        blacklist=blacklist,
        recursive=recursive
    )
