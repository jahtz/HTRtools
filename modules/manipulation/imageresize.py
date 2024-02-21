from pathlib import Path

import click
from PIL import Image


def imageresize(input_dir: Path, output_dir: Path | None, input_regex: str, output_suffix: str | None, height: int) -> None:
    if output_dir is not None and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    imgs = list(input_dir.glob(input_regex))
    with click.progressbar(imgs, label='Resize image', show_pos=True, item_show_func=lambda x: f'{f"({x.name})" if x is not None else ""}') as images:
        for image in images:
            with Image.open(image) as img:
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                resized = img.resize((new_width, height), Image.LANCZOS)
            if output_dir is None:
                resized.save(image)
            else:
                fn = image.name if output_suffix is None else f'{image.name.split('.')[0]}{output_suffix}'
                resized.save(output_dir.joinpath(fn))


@click.command('imageresize', short_help='Resizes images.')
@click.help_option('--help', '-h')
@click.argument(
    'input_dir',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.argument(
    'output_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=False
)
@click.option(
    '-i', '--input_regex',
    help='Input filename regular expression (example: *.orig.png).',
    type=str,
    default='*',
    show_default=True,
    required=False
)
@click.option(
    '-o', '--output_suffix',
    help='Replaces all suffixes after first dot. Only with OUTPUT argument set.',
    type=str,
    required=False,
)
@click.option(
    '-s', '--size',
    help='Set height of output images in pixels.',
    type=int,
    required=True
)
def imageresize_cli(input_dir: str, output_dir: str | None, input_regex: str, output_suffix: str | None, size: int) -> None:
    """
    Resizes images.

    Overwrites original images if OUTPUT_DIR is not set.
    """
    imageresize(
        input_dir=Path(input_dir),
        output_dir=None if output_dir is None else Path(output_dir),
        input_regex=input_regex,
        output_suffix=None if output_suffix is None else (output_suffix if output_suffix.startswith(".") or output_suffix == '' else f".{output_suffix}"),
        height=size
    )
