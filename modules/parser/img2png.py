from pathlib import Path

import click
from PIL import Image


def img2png(
        input_dir: Path,
        output_dir: Path,
        input_suffix: str,
        output_suffix: str,
        height: int | None,
        recursive: bool,
        number: bool
) -> None:
    output_dir.mkdir(exist_ok=True)
    images = list(input_dir.glob(f'{"**/" if recursive else ""}*{input_suffix}'))
    images.sort()
    with click.progressbar(images, label='Convert images', show_pos=True) as imgs:
        for i, image in enumerate(imgs):
            if number:
                out_path = output_dir.joinpath(f'{(i +1):04d}{output_suffix}.png')
            else:
                out_path = output_dir.joinpath(f'{image.name.replace(input_suffix, f"{output_suffix}")}.png')
            img = Image.open(image)
            if height is not None:
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
            img.save(out_path)


@click.command('img2png', short_help='Converts any image file formats to PNG file.')
@click.help_option('--help', '-h')
@click.argument(
    'input_dir',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True
)
@click.argument(
    'output_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=True
)
@click.option(
    '-i', '--input_suffix',
    help='Input file suffix.',
    type=str,
    default='.jpg',
    show_default=True,
    required=False
)
@click.option(
    '-o', '--output_suffix',
    help='Output file suffix between filename and ".png".',
    type=str,
    default='',
    show_default=False,
    required=False
)
@click.option(
    '-s', '--size',
    help='Set height of output images in pixels. Defaults to input height.',
    type=int,
    required=False
)
@click.option(
    '-r', '--recursive',
    help='Walks INPUT_DIR recursively.',
    is_flag=True,
    type=bool,
    required=False
)
@click.option(
    '-n', '--number',
    help='number filenames.',
    is_flag=True,
    type=bool,
    required=False
)
def img2png_cli(
        input_dir: str,
        output_dir: str,
        input_suffix: str,
        output_suffix: str,
        size: int | None,
        recursive: bool,
        number: bool
) -> None:
    """
    Converts any image file formats to PNG file.
    """
    img2png(
        input_dir=Path(input_dir),
        output_dir=Path(output_dir),
        input_suffix=input_suffix if input_suffix.startswith(".") else f".{input_suffix}",
        output_suffix=output_suffix if output_suffix.startswith(".") or output_suffix == '' else f".{output_suffix}",
        height=size,
        recursive=recursive,
        number=number
    )
