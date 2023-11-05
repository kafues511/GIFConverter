from dataclasses import dataclass
from typing import Union, Iterator, Any
 
 
__all__ = [
    "GridUtil",
]


@dataclass
class GridUtil:
    __column:Union[int, Iterator[int]]
    __row:Union[int, Iterator[int]]
    __columnspan:Union[int, Iterator[int]]
    __sticky:Union[str, Iterator[str]]

    def __init__(
        self,
        column:Union[int, tuple[int, ...]],
        row:Union[int, tuple[int, ...]],
        columnspan:Union[int, tuple[int, ...]],
        sticky:Union[int, tuple[str, ...]],
    ) -> None:
        self.__column = iter(column) if self.is_tuple(column) else column
        self.__row = iter(row) if self.is_tuple(row) else row
        self.__columnspan = iter(columnspan) if self.is_tuple(columnspan) else columnspan
        self.__sticky = iter(sticky) if self.is_tuple(sticky) else sticky

    @staticmethod
    def is_tuple(value:Any) -> bool:
        if isinstance(value, tuple):
            return len(value) > 0
        return False

    @property
    def column(self) -> int:
        return next(self.__column) if isinstance(self.__column, Iterator) else self.__column

    @property
    def row(self) -> int:
        return next(self.__row) if isinstance(self.__row, Iterator) else self.__row

    @property
    def columnspan(self) -> int:
        return next(self.__columnspan) if isinstance(self.__columnspan, Iterator) else self.__columnspan

    @property
    def sticky(self) -> str:
        return next(self.__sticky) if isinstance(self.__sticky, Iterator) else self.__sticky
