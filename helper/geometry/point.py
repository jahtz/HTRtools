from typing import Self


class Point:
    """
    0,0 -- x,0
     |      |
     | PAGE |
     |      |
    0,y -- x,y
    """
    def __init__(self, x: int, y: int):
        self._x: int = x
        self._y: int = y

    def __str__(self):
        return f'Point({self._x}, {self._y})'

    def __repr__(self):
        return f'Point({self._x}, {self._y})'

    @property
    def x(self) -> int:
        """ Get the x-coordinate of the point. """
        return self._x

    @x.setter
    def x(self, x: int):
        """ Set the x-coordinate of the point. """
        self._x = x

    @property
    def y(self) -> int:
        """ Get the y-coordinate of the point. """
        return self._y

    @y.setter
    def y(self, y: int):
        """ Set the y-coordinate of the point. """
        self._y = y

    @classmethod
    def from_string(cls, xy: str) -> Self:
        """ Creates a Point object from a string of the form 'x,y'. """
        x, y = map(int, xy.split(','))
        return cls(x, y)

    @classmethod
    def from_int(cls, x: int, y: int) -> Self:
        """ Creates a Point object from two integers. """
        return cls(x, y)

    @classmethod
    def from_tuple(cls, xy: tuple) -> Self:
        """ Creates a Point object from a tuple of two integers of the form (x, y)."""
        x, y = xy
        return cls(int(x), int(y))

    def to_string(self) -> str:
        """ Returns a string of the form 'x,y'. """
        return f'{self._x},{self._y}'

    def to_tuple(self) -> tuple[int, int]:
        """ Returns a tuple of the form (x, y). """
        return self._x, self._y
