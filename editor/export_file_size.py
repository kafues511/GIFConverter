import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

import math
from typing import Union, Optional, Callable

from editor.grid_util import *


__all__ = [
    "ExportFileSize",
]


class ExportFileSize:
    def __init__(
        self,
        master:tk.Misc,
        column:Union[int, tuple[int, int]],
        row:Union[int, tuple[int, int]],
        columnspan:Union[int, tuple[int, int]] = (1, 1),
        sticky:Union[str, tuple[str, str, str]] = (EW, EW),
        callback_export:Optional[Callable[[], None]] = None,
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        self.filesize_var = ttk.StringVar(value=f"{math.nan}")

        label = ttk.Label(master, text="Export file size")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="出力結果のファイルサイズ")

        self.entry = ttk.Entry(master, textvariable=self.filesize_var, state=READONLY)
        self.entry.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)
