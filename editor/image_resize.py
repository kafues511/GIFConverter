import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from typing import Union

from editor.grid_util import *


__all__ = [
    "ImageResize",
]


class ImageResize:
    def __init__(
        self,
        master:tk.Misc,
        column:Union[int, tuple[int, int]],
        row:Union[int, tuple[int, int]],
        columnspan:Union[int, tuple[int, int]] = (1, 1),
        sticky:Union[str, tuple[str, str]] = (EW, EW),
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        label = ttk.Label(master, text="Image resize")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="リサイズ", delay=100)

        # リサイズ一覧
        values = ["25.0 %", "50.0 %", "75.0 %", "100.0 %", "125.0 %", "150.0 %", "175.0 %", "200.0 %"]

        self.combobox = ttk.Combobox(master, values=values, state=READONLY)
        self.combobox.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)
        self.combobox.set("100.0 %")
        self.combobox.bind("<<ComboboxSelected>>", lambda event: self.combobox.selection_clear())

    @property
    def image_resize(self) -> float:
        """画像のリサイズを取得

        Returns:
            float: 画像のリサイズ
        """
        return float(self.combobox.get()[:-2]) * 0.01
