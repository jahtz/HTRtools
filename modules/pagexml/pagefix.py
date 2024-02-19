from pathlib import Path
from typing import Self

import click
from lxml import etree

from .pagexml import Coordinate


class PageFix:
    def __init__(self, fp: Path, parser: etree.XMLParser) -> None:
        self.__fp: Path = fp
        self.root = etree.parse(self.__fp.as_posix(), parser).getroot()

    def set_relative_image_filename(self) -> Self:
        """
        Updates imageFilename attribute of Page Elements

        :return: reference to current object
        """
        filename = self.__fp.name.replace('.xml', '.png')
        page = self.root.find(".//{*}Page")
        page.set('imageFilename', filename)
        return self

    def merge_regions(self) -> Self:
        """
        Merges all regions with same region coordinates

        :return: reference to current object
        """
        page = self.root.find(".//{*}Page")
        found_regions = {}

        for text_region in self.root.findall('.//{*}TextRegion'):
            coordinates = text_region.find('./{*}Coords').get('points')
            if coordinates in found_regions:  # if region with same coordinates already found: append to existing
                for text_line in text_region.findall('./{*}TextLine'):
                    found_regions[coordinates].append(text_line)
            else:  # else add to found regions list
                text_region.set('id', f'r_{len(found_regions):04d}')  # set id to index
                found_regions[coordinates] = text_region
            # after analyze, remove region with content from page
            text_region.getparent().remove(text_region)

        # add regions back to page element
        # TODO: Improve order by requesting column count, taking center of region and order by that
        for coords, region in found_regions.items():
            page.append(region)
        return self

    def create_reading_order(self) -> Self:
        """
        Creates a readingOrder Element

        :return: reference to current object
        """
        page = self.root.find("./{*}Page")
        reading_order = []

        # get reading order by order in xml
        for idx, text_region in enumerate(self.root.findall(".//{*}TextRegion")):
            new_id = f'r_{idx:04d}'
            text_region.set('id', new_id)
            reading_order.append(new_id)

        # remove existing reading order
        existing_reading_order = page.find('./{*}ReadingOrder')
        if existing_reading_order is not None:
            existing_reading_order.getparent().remove(existing_reading_order)

        # add new reading order
        reading_order_element = etree.Element("ReadingOrder")
        ordered_group_element = etree.SubElement(reading_order_element, "OrderedGroup")
        ordered_group_element.set("id", "g0")
        for idx, elem in enumerate(reading_order):
            region_ref_index_elem = etree.SubElement(ordered_group_element, "RegionRefIndexed")
            region_ref_index_elem.set("index", str(idx))
            region_ref_index_elem.set("regionRef", elem)
        page.insert(0, reading_order_element)
        return self

    def fix_region_type(self) -> Self:
        """
        Updates regions type attribute by custom attribute

        :return: reference to current object
        """
        for text_region in self.root.findall(".//{*}TextRegion"):
            custom = text_region.get("custom")
            if not custom:
                continue
            _type = custom.replace('structure {type:', '')
            _type = _type.replace(';}', '')
            text_region.set('type', _type)
        return self

    def fix_negative_coordinates(self) -> Self:
        """
        Replaces all negative coordinates with zeros

        :return: reference to current object
        """
        for text_region in self.root.findall('.//{*}TextRegion'):
            for text_line in text_region.findall('./{*}TextLine'):
                coordinates = text_line.find("./{*}Coords")
                points = PageFix.string_to_coordinates(coordinates.get("points"))
                for point in points:
                    if point.x < 0: point.x = 0
                    if point.y < 0: point.y = 0
                coordinates.set('points', PageFix.coordinates_to_string(points))
        return self

    def fix_line_order(self) -> Self:
        """
        Sorts all lines of each region by its y coordinates and cuts of all spikes above prior line

        :return: reference to current object
        """
        for text_region in self.root.findall('.//{*}TextRegion'):
            # sort lines of text region by their baseline center y coordinate
            text_region[:] = sorted(text_region, key=lambda line: PageFix.center_of_baseline(line).y)

            min_y = 0  # min y coordinate of previous text line
            for text_line in text_region.findall("./{*}TextLine"):
                coordinates = text_line.find("./{*}Coords")
                points = PageFix.string_to_coordinates(coordinates.get("points"))
                for point in points:  # set all y coordinates at least one pixel lower than previous lines highest y coordinate
                    if point.y <= min_y:
                        point.y = min_y + 1
                min_y = min([p.y for p in points])  # calculate highest y coordinate of current text line
                coordinates.set('points', PageFix.coordinates_to_string(points))
        return self

    def save(self, path: Path | None = None) -> None:
        """
        Save changes. Overwrites old file of writes to new file

        :param path: if set, writes changes to new file
        :return: nothing
        """
        with open(self.__fp if path is None else path, 'wb') as f:
            f.write(etree.tostring(self.root, pretty_print=True))

    @classmethod
    def center_of_baseline(cls, line) -> Coordinate:
        """
        Returns center of Baseline of TextLine Element

        :param line: TextLine Element
        :return: Center Coordinate
        """
        baseline = line.find('./{*}Baseline')
        if baseline is None:
            return Coordinate('0,0')
        points = cls.string_to_coordinates(baseline.get('points'))
        return cls.center_of_polygon(points)

    @staticmethod
    def string_to_coordinates(coords_str: str) -> list[Coordinate]:
        """
        Parses a string of type 'x1,y1 x2,y2 ...' to list of Coordinates

        :param coords_str: PageXML coordinates string
        :return: list of Coordinates
        """
        return [Coordinate(xy) for xy in coords_str.split(' ')]

    @staticmethod
    def coordinates_to_string(coords: list[Coordinate]) -> str:
        """
        Parses a list of Coordinates to a string of type 'x1,y1 x2,y2 ...'

        :param coords: List of Coordinates
        :return: PageXML coordinates string
        """
        return ' '.join([str(x) for x in coords])

    @staticmethod
    def center_of_polygon(polygon: list[Coordinate]) -> Coordinate:
        """
        Returns center of a polygon

        :param polygon: list of Coordinates representing a polygon
        :return: center Coordinate
        """
        x = int(sum([coord.x for coord in polygon]) / len(polygon))
        y = int(sum([coord.y for coord in polygon]) / len(polygon))
        return Coordinate(f'{x},{y}')


@click.command('pagefix', short_help='Fix invalid PageXML documents.')
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
    '-f', '--image_filename',
    help='Changes imageFilename attribute of Page element from absolute to relative.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-m', '--merge_regions',
    help='Merges TextRegion elements with same coordinates.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-r', '--reading_order',
    help='Adding or updating ReadingOrder element.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-t', '--region_type',
    help='Adding or fixing type attribute to Page element.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-c', '--negative_coords',
    help='Sets all negative coordinates of TextLine elements to 0.',
    is_flag=True,
    type=bool,
    default=False
)
@click.option(
    '-l', '--line_order',
    help='Fixing TextLine element order by their y coordinates.',
    is_flag=True,
    type=bool,
    default=False
)
def pagefix_cli(input_dir: str, output_dir: str | None, image_filename: bool, merge_regions: bool, reading_order: bool,
                region_type: bool, negative_coords: bool, line_order: bool):
    """
    Fix invalid PageXML documents.

    If OUTPUT_DIR is not set, script will overwrite old xml files.

    Recommended options: -cfrt
    """
    parser = etree.XMLParser(remove_blank_text=True)
    files = Path(input_dir).glob('*.xml')
    click.echo(f'fixing {len(list(files))} files')
    for file in files:
        pf = PageFix(file, parser)
        if image_filename:
            pf.set_relative_image_filename()
        if merge_regions:
            pf.merge_regions()
        if reading_order:
            pf.create_reading_order()
        if region_type:
            pf.fix_region_type()
        if negative_coords:
            pf.fix_negative_coordinates()
        if line_order:
            pf.fix_line_order()
        pf.save(None if output_dir is None else Path(output_dir).joinpath(file.name))
    click.echo('Done!')


if __name__ == '__main__':
    pass
