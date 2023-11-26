import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from typing import Union

from editor.grid_util import *


__all__ = [
    "QuantizeKMeans",
]


class QuantizeKMeans:
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

        self.kmeans_var = ttk.StringVar(value="0")

        label = ttk.Label(master, text="Quantize k-mean")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="クラスタ数の指定")

        self.entry = ttk.Entry(master, textvariable=self.kmeans_var, validate="all", validatecommand=(master.register(self.set_kmeans), "%P"))
        self.entry.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)

    def set_kmeans(self, new_kmeans:str) -> bool:
        """クラスタ数をセット

        Args:
            new_kmeans (str): 新しいクラスタ数

        Returns:
            bool: 0未満やint型以外が入力された場合はFalseを返します。
        """
        try:
            return new_kmeans == "" or int(new_kmeans) >= 0
        except Exception as e:
            return False

    @property
    def kmeans(self) -> int:
        """クラスタ数を取得

        Returns:
            int: クラスタ数
        """
        if (value:=self.kmeans_var.get()) == "":
            return 0
        return int(value)
