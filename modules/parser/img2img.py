from pathlib import Path

import click
from PIL import Image


def img2img(images: Path, out_dir: Path, in_suffix: str, out_suffix: str, height: int | None):
    """
    Converts image files of type in_suffix to out_suffix

    :param images: Path to directory or file
    :param out_dir: Directory for output files
    :param in_suffix: suffix of input files, starting with ., ignored if IMAGES points to a file
    :param out_suffix: suffix of output files, starting with .
    :param height: Height of converted files in pixels, keep original height if set to None
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    if images.is_dir():
        img_list = sorted(list(images.glob(f'*{in_suffix}')))
    else:
        img_list = [images]
    with click.progressbar(img_list, label='Convert images', show_pos=True, show_eta=True, show_percent=True) as imgs:
        for image in imgs:
            out_path = out_dir.joinpath(f'{image.name.replace(in_suffix, out_suffix)}')
            img = Image.open(image)
            if height is not None:
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
            img.save(out_path)


@click.command('img2img', short_help='Convert image files.')
@click.help_option('--help', '-h')
@click.argument(
    'images',
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    required=True
)
@click.argument(
    'out_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=True
)
@click.option(
    '-i', '--input', '_input',
    help='Input file suffix. Ignored if IMAGES points to a file.',
    type=str,
    required=True,
    default='.png'
)
@click.option(
    '-o', '--output',
    help='Output file suffix.',
    type=str,
    required=True,
    default='.png'
)
@click.option(
    '-s', '--size',
    help='Set height of output images in pixels. Defaults to original height.',
    type=int,
    required=False
)
def img2img_cli(images: str, out_dir: str, _input: str, output: str, size: int | None):
    """
    Converts image file with INPUT format to OUTPUT format.
    """
    img2img(
        images=Path(images),
        out_dir=Path(out_dir),
        in_suffix=_input if _input.startswith('.') else f'.{_input}',
        out_suffix=output if output.startswith('.') else f'.{output}',
        height=size
    )