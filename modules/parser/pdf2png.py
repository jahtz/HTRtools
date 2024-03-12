from pathlib import Path

import click
import fitz
from PIL import Image


def pdf2png(input_pdf: Path, output_dir: Path, output_suffix: str, height: int | None, dpi: int) -> None:
    output_dir.mkdir(exist_ok=True, parents=True)
    fs = fitz.open(input_pdf)
    with click.progressbar(fs, label='Convert page', show_pos=True) as pages:
        for i, page in enumerate(pages):
            pixmap = page.get_pixmap(dpi=dpi)
            outfile = output_dir.joinpath(f'{(i + 1):04d}{output_suffix}.png')
            pixmap.save(outfile)
            if height is not None:
                img = Image.open(outfile)
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
                img.save(outfile)


@click.command('pdf2png', short_help='Converts PDF file to PNG files.')
@click.help_option('--help', '-h')
@click.argument(
    'input_pdf',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True
)
@click.argument(
    'output_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=True
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
    help='Set height of output images in pixels. Defaults to original height.',
    type=int,
    required=False
)
@click.option(
    '-d', '--dpi',
    help='DPI for PDF scanning.',
    type=int,
    required=False,
    default=300,
    show_default=True
)
def pdf2png_cli(input_pdf: str, output_dir: str, output_suffix: str, size: int | None, dpi: int) -> None:
    """
    Converts PDF file to PNG images, numerated by page number.
    """
    pdf2png(
        input_pdf=Path(input_pdf),
        output_dir=Path(output_dir),
        output_suffix=output_suffix if output_suffix.startswith(".") or output_suffix == '' else f".{output_suffix}",
        height=size,
        dpi=dpi
    )