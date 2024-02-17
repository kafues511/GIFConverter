import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from typing import Union
from PIL import Image

from editor.grid_util import *


__all__ = [
    "QuantizeMethod",
]


class QuantizeMethod:
    def __init__(
        self,
        master:tk.Misc,
        column:Union[int, tuple[int, int, int, int]],
        row:Union[int, tuple[int, int, int, int]],
        columnspan:Union[int, tuple[int, int, int, int]] = (1, 1, 1, 1),
        sticky:Union[str, tuple[str, str, str, str]] = (EW, EW, EW, EW),
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        label = ttk.Label(master, text="Quantize method")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(10, 5), sticky=grid.sticky)
        ToolTip(label, text="量子化の種類\nNONE:圧縮なし\nMEDIANCUT:品質(高)/圧縮(低)\nFASTOCTREE:品質(低)/圧縮(高)", delay=100)

        self.quantize_method_var = ttk.IntVar(value=int(Image.Quantize.MEDIANCUT))

        mediancut_radiobutton = ttk.Radiobutton(master, text="None", variable=self.quantize_method_var, value=-1)
        mediancut_radiobutton.grid(column=grid.column+1, row=grid.row, pady=(10, 5), sticky=grid.sticky)
        ToolTip(mediancut_radiobutton, text="圧縮なし", delay=100)

        mediancut_radiobutton = ttk.Radiobutton(master, text="Median cut", variable=self.quantize_method_var, value=int(Image.Quantize.MEDIANCUT))
        mediancut_radiobutton.grid(column=grid.column+2, row=grid.row, pady=(10, 5), sticky=grid.sticky)
        ToolTip(mediancut_radiobutton, text="品質(高)/圧縮(低)", delay=100)

        fastoctree_radiobutton = ttk.Radiobutton(master, text="Fast octree", variable=self.quantize_method_var, value=int(Image.Quantize.FASTOCTREE))
        fastoctree_radiobutton.grid(column=grid.column+3, row=grid.row, pady=(10, 5), sticky=grid.sticky)
        ToolTip(fastoctree_radiobutton, text="品質(低)/圧縮(高)", delay=100)

    @property
    def quantize_method(self) -> int:
        """量子化の種類を取得

        Returns:
            int: 量子化の種類
        """
        return self.quantize_method_var.get()
