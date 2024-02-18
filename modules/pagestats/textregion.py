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

    def increment_lines(self) -> None:
        self.__lines += 1