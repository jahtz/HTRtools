from dataclasses import dataclass


@dataclass
class Coordinate:
    x: int
    y: int

    """
    0,0 -- x,0
     |      |
     |  A4  |
     |      |
    0,y -- x,y
    """

    def __init__(self, xy: str):
        self.x, self.y = map(int, xy.split(','))

    def __str__(self):
        return f'{self.x},{self.y}'


class TextRegion:
    def __init__(self, _id: str, _type: str) -> None:
        self.__id: str = _id
        self.__type: str = _type
        self.__lines: int = 0

    def __str__(self) -> str:
        return f'TextRegion(ID: {self.__id}, type: {self.__type}) with {self.__lines} TextLines'

    def get_id(self) -> str:
        return self.__id

    def get_type(self) -> str:
        return self.__type

    def get_lines(self) -> int:
        return self.__lines

    def set_lines(self, lines: int) -> None:
        self.__lines = lines
