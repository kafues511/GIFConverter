import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from typing import Union, Optional, Callable

from editor.grid_util import *


__all__ = [
    "ExportState",
]


class ExportState:
    def __init__(
        self,
        master:tk.Misc,
        column:Union[int, tuple[int, int, int]],
        row:Union[int, tuple[int, int, int]],
        columnspan:Union[int, tuple[int, int, int]] = (1, 1, 1),
        sticky:Union[str, tuple[str, str, str]] = (EW, EW, EW),
        callback_export:Optional[Callable[[], None]] = None,
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        label = ttk.Label(master, text="Export state")
        label.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)
        ToolTip(label, text="出力結果によってボタンの色が変わります。")

        self.progressbar = ttk.Progressbar(master, mode=DETERMINATE, bootstyle=(STRIPED, PRIMARY))
        self.progressbar.grid(column=grid.column+1, row=grid.row, columnspan=grid.columnspan, padx=(0, 10), pady=(5, 0), sticky=grid.sticky)

        self.button = ttk.Button(master, text="Export", bootstyle=(SOLID, PRIMARY), state=DISABLED, command=callback_export)
        self.button.grid(column=grid.column+2, row=grid.row, columnspan=grid.columnspan, pady=(5, 0), sticky=grid.sticky)

    def set_button_state(self, state:str) -> None:
        """ボタンの状態をセットします。

        Args:
            state (str): 状態
        """
        self.button.configure(state=state)

    def start(self) -> None:
        """出力開始
        """
        self.progressbar.start()
        self.button.configure(state=DISABLED)

    def end(self, is_success:bool) -> None:
        """出力終了

        Args:
            is_success (bool): 出力の成否
        """
        self.progressbar.stop()
        self.button.configure(state=ACTIVE, bootstyle=(SOLID, (SUCCESS if is_success else DANGER)))
