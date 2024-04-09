from pathlib import Path

import click
import fitz
from PIL import Image


def pdf2img(pdf: Path, out_dir: Path, output: str, height: int | None, dpi: int):
    """
    Converts a pdf file to image files.

    :param pdf: input pdf file path
    :param out_dir: output directory for image files
    :param output: output image file suffix, starting with '.'
    :param height: output image height in pixels. Keep original height if set to None
    :param dpi: pdf scan dpi
    """
    out_dir.mkdir(exist_ok=True, parents=True)

    fs = fitz.open(pdf)
    with click.progressbar(fs, label='Convert images', show_pos=True, show_eta=True, show_percent=True) as pages:
        for i, page in enumerate(pages):
            pixmap = page.get_pixmap(dpi=dpi)
            outfile = out_dir.joinpath(f'{(i + 1):04d}{output}')
            pixmap.save(outfile)
            if height is not None:
                img = Image.open(outfile)
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
                img.save(outfile)


@click.command('pdf2img', short_help='Convert PDF file to image files.')
@click.help_option('--help', '-h')
@click.argument(
    'pdf',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True
)
@click.argument(
    'out_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=True
)
@click.option(
    '-o', '--output',
    help='Output image file suffix.',
    type=str,
    default='.png',
    show_default=True,
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
def pdf2img_cli(pdf: str, out_dir: str, output: str, size: int | None, dpi: int):
    """
    Converts PDF file to PNG images, numerated by page number.
    """
    pdf2img(
        pdf=Path(pdf),
        out_dir=Path(out_dir),
        output=output if output.startswith('.') else f'.{output}',
        height=size,
        dpi=dpi
    )
