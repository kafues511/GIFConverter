import tkinter as tk
from tkinter.filedialog import askopenfilename
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from pathlib import Path
from typing import Union, Optional, Callable

from editor.grid_util import *


__all__ = [
    "InputVideoFile",
]


class InputVideoFile:
    # 対応している動画の拡張子
    FILETYPES = tuple([("VideoFile", "*.mp4 *.avi")])

    def __init__(
        self,
        master:tk.Misc,
        column:Union[int, tuple[int, int, int]],
        row:Union[int, tuple[int, int, int]],
        columnspan:Union[int, tuple[int, int, int]] = (1, 1, 1),
        sticky:Union[str, tuple[str, str, str]] = (EW, EW, EW),
        callback_path_update:Optional[Callable[[str], None]]=None,
        *args,
        **kwargs,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        self.path_var = ttk.StringVar(value=Path().absolute().as_posix())

        label = ttk.Label(master, text="Input path")
        label.grid(column=grid.column, row=grid.row, sticky=grid.sticky)
        ToolTip(label, text="GIF変換する動画を指定", delay=100)

        entry = ttk.Entry(master, textvariable=self.path_var)
        entry.grid(column=grid.column+1, row=grid.row, columnspan=2, padx=(0, 10), sticky=grid.sticky)

        button = ttk.Button(master, text="Browse", bootstyle=(SOLID, PRIMARY), command=self.on_browse)
        button.grid(column=grid.column+2, row=grid.row, sticky=grid.sticky)

        # register callback
        self.callback_path_update = callback_path_update 

        # パスを入力した際のイベント登録
        entry.bind("<KeyRelease>", self.on_path_update)

    def on_browse(self) -> None:
        if (path:=askopenfilename(filetypes=self.FILETYPES)):
            # パスの更新
            self.path_var.set(path)

            # パス更新時のイベント呼び出し
            self.on_path_update()

    def on_path_update(self, event:Optional[tk.Event]=None) -> None:
        if self.callback_path_update is not None:
            self.callback_path_update(self.path)

    @property
    def path(self) -> str:
        return self.path_var.get()
