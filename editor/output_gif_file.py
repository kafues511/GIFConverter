import tkinter as tk
from tkinter.filedialog import asksaveasfilename
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from editor.grid_util import *


__all__ = [
    "OutputGifFile",
]


class OutputGifFile:
    # 対応している動画の拡張子
    FILETYPES = tuple([("GifFile", "*.gif")])

    def __init__(
        self,
        master:tk.Misc,
        column:int,
        row:int,
        columnspan:tuple[int, int, int] = (1, 1, 1),
        sticky:tuple[str, str, str] = (EW, EW, EW),
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        self.path_var = ttk.StringVar(value="")

        label = ttk.Label(master, text="Output path")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="GIFの出力先\n未指定の場合は動画と同じ場所に保存します。", delay=100)

        entry = ttk.Entry(master, textvariable=self.path_var)
        entry.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)

        button = ttk.Button(master, text="Browse", command=self.on_browse, bootstyle=(SOLID, PRIMARY))
        button.grid(column=grid.column+2, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)

    def on_browse(self) -> None:
        if (path:=asksaveasfilename(title="保存", filetypes=self.FILETYPES)):
            self.path_var.set(path)

    @property
    def path(self) -> str:
        return self.path_var.get()
