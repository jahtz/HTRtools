from pathlib import Path

import click

from pagexml import PageXML, Element
from helper.page import get_page_regions, get_coords, get_coords_element, get_region_elements


class PageFix:
    def __init__(self, in_fp: Path, out_fp: Path):
        self._pxml = PageXML.from_xml(in_fp)
        self._out_fp = out_fp

    def set_relative_image_filename(self):
        """
        Updates imageFilename attribute of each page element from absolute to filename
        """
        for page in self._pxml:
            page['imageFilename'] = Path(page['imageFilename']).name

    def merge_regions(self):
        """
        Merge all regions with same region coordinates
        """
        for page in self._pxml:
            found_regions: dict[str, Element] = {}
            for region in get_page_regions(page):
                coords = get_coords(region).to_page_coords()
                if coords in found_regions:
                    for element in region:
                        found_regions[coords].add_element(element)
                else:
                    region['id'] = f'r_{len(found_regions):04d}'
                    found_regions[coords] = region
                page.remove_element(region)
            for coords, region in found_regions.items():
                page.add_element(region)

    def reading_order(self):
        """
        Create reading order element and add regions
        """
        for page in self._pxml:
            ro = []
            for region in get_page_regions(page):
                ro.append(region['id'])
            page.reading_order = ro

    def region_type(self):
        """
        Updates region type from custom attribute
        """
        for page in self._pxml:
            for region in get_page_regions(page):
                if (custom := region['custom']) is not None:
                    _type = custom.replace('structure {type:', '')
                    _type = _type.replace(';}', '')
                    region['type'] = _type

    def negative_coordinates(self):
        """
        Replace all negative coordinates with zeros
        """
        for page in self._pxml:
            for region in get_page_regions(page):
                coords = get_coords(region)
                for point in coords:
                    if point.x < 0:
                        point.x = 0
                    if point.y < 0:
                        point.y = 0
                get_coords_element(region)['points'] = coords.to_page_coords()

    def line_order(self):
        """
        Sort all lines of each region by its y coordinates
        """
        for page in self._pxml:
            for region in get_page_regions(page):
                region.elements.sort(key=lambda e: get_coords(e).center().y)

    def spikes(self):
        """
        Remove spikes from elements coordinates
        """
        for page in self._pxml:
            for region in get_page_regions(page):
                min_y = 0  # min y coordinate of previous text line
                for element in get_region_elements(region):
                    coords = get_coords(element)
                    for point in coords:
                        if point.y <= min_y:
                            point.y = min_y + 1
                    min_y = min([p.y for p in coords])
                    get_coords_element(element)['points'] = coords.to_page_coords()

    def save(self):
        """
        Save changes
        """
        self._pxml.to_xml(self._out_fp)


@click.command('pagefix', short_help='Fix invalid PageXML documents')
@click.help_option('--help', '-h')
@click.argument(
    'input',
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    required=True
)
@click.argument(
    'out_dir',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=False
)
@click.option(
    '-f', '--filename',
    help='Changes imageFilename attribute of Page element from absolute to relative.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-r', '--regions',
    help='Merges TextRegion elements with same coordinates.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-o', '--order',
    help='Adding or updating ReadingOrder element.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-t', '--type',
    help='Adding or fixing type attribute to Page element.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-c', '--coords',
    help='Sets all negative coordinates of TextLine elements to 0.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-l', '--lines',
    help='Fixing TextLine element order by their y coordinates.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
@click.option(
    '-s', '--spikes',
    help='Removes element mask spikes.',
    is_flag=True,
    type=click.BOOL,
    default=False
)
def pagefix_cli(_input: str, out_dir: str | None, filename: bool, regions: bool, order: bool, _type: bool,
                coords: bool, lines: bool, spikes: bool):
    """
    Fix invalid PageXML documents.

    If OUTPUT_DIR is not set, script will overwrite old xml files.

    Recommended options: -cfot
    """
    in_fp = Path(_input)
    if in_fp.is_dir():
        files = in_fp.glob('*.xml')
    else:
        files = [in_fp]
    with click.progressbar(files, label='Fixing PageXML', show_pos=True, show_eta=True, show_percent=True) as fs:
        for file in fs:
            pf = PageFix(file, file if out_dir is None else Path(out_dir).joinpath(file.name))
            if filename:
                pf.set_relative_image_filename()
            if regions:
                pf.merge_regions()
            if order:
                pf.reading_order()
            if _type:
                pf.region_type()
            if coords:
                pf.negative_coordinates()
            if lines:
                pf.line_order()
            if spikes:
                pf.spikes()
            pf.save()
