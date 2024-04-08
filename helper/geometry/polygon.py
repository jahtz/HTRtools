from typing import Self

from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint

from .point import Point


class Polygon:
    def __init__(self, points: list[Point]):
        self._points: list[Point] = points

    def __str__(self):
        return f'Polygon({" ".join(map(str, self._points))})'

    def __repr__(self):
        return ' '.join(map(str, self._points))

    def __iter__(self) -> Self:
        """ Iterate through the list of points """
        self.__n = 0
        return self

    def __next__(self) -> Point:
        """ Iterate through the list of points """
        if self.__n < len(self._points):
            point = self._points[self.__n]
            self.__n += 1
            return point
        else:
            raise StopIteration

    @classmethod
    def from_page_coords(cls, coords: str) -> Self:
        """ Creates Polygon object from PageXML coords string """
        points = list(map(Point.from_string, coords.split(' ')))
        return cls(points)

    def to_page_coords(self) -> str:
        """ Returns coordinates as a string compatible with PageXML """
        return ' '.join([p.to_string() for p in self._points])

    @classmethod
    def from_bbox(cls, coords: list[int | str]) -> Self:
        """ Creates Polygon object from a bbox in list format """
        return cls([
            Point.from_int(int(coords[0]), int(coords[1])),
            Point.from_int(int(coords[0]) + int(coords[2]), int(coords[1])),
            Point.from_int(int(coords[0]) + int(coords[2]), int(coords[1]) + int(coords[3])),
            Point.from_int(int(coords[0]), int(coords[1]) + int(coords[3]))
        ])
    
    @classmethod
    def from_coco(cls, coords: list[int]) -> Self:
        return cls(list([Point.from_int(int(coords[i]), int(coords[i+1])) for i in range(0, len(coords), 2)]))

    @classmethod
    def from_tuple_list(cls, coords: list[tuple]) -> Self:
        """ Creates Polygon from list of tuples of type (x, y) """
        return cls(list([Point.from_tuple(x) for x in coords]))

    def to_tuple_list(self) -> list[tuple]:
        """ Returns a list of tuples in (x, y) format """
        return list([x.to_tuple() for x in self._points])

    @classmethod
    def from_point_list(cls, coords: list[Point]):
        """ Creates Polygon object from a list of Point objects """
        return cls(coords)

    def to_point_list(self) -> list[Point]:
        """ Returns a list with Point objects """
        return self._points.copy()

    def center(self) -> Point:
        """ Returns geometric center of polygon """
        center = ShapelyPolygon(self.to_tuple_list()).centroid
        return Point.from_tuple((round(center.x), round(center.y)))

    def contains(self, point: Point | tuple) -> bool:
        """ Checks, if a point is within this polygon. Accepts Point object or tuple (x, y)"""
        return ShapelyPolygon(self.to_tuple_list()).contains(ShapelyPoint((point.x, point.y)))
