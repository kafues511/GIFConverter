import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from typing import Union

from editor.grid_util import *


__all__ = [
    "PlaySpeed",
]


class PlaySpeed:
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

        label = ttk.Label(master, text="Play speed")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="再生速度", delay=100)

        # 再生速度一覧
        values = ["0.25", "0.5", "0.75", "1.0", "1.25", "1.5", "1.75", "2.0"]

        self.combobox = ttk.Combobox(master, values=values, state=READONLY)
        self.combobox.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)
        self.combobox.set("1.0")
        self.combobox.bind("<<ComboboxSelected>>", lambda event: self.combobox.selection_clear())

    @property
    def play_speed(self) -> float:
        """再生速度を取得

        Returns:
            float: 再生速度
        """
        return float(self.combobox.get())
