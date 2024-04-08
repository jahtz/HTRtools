from pagexml import PageXML, Page, Element, ElementType
from helper.geometry import Polygon, Point


def get_page_regions(page: Page) -> list[Element]:
    return list([r for r in page if r.is_region()])


def get_region_elements(region: Element) -> list[Element]:
    return list([e for e in region if not e.is_region()])


def get_coords(element: Element) -> Polygon:
    for e in element:
        return Polygon.from_page_coords(e['points'])
    return Polygon.from_tuple_list([(0, 0), (0, 0)])


def get_coords_element(element: Element) -> Element | None:
    for e in element:
        return e
    return None
