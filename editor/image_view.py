import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import threading as th
from PIL import Image, ImageTk
from itertools import cycle

from editor.grid_util import *


__all__ = [
    "ImageView",
]


class ImageView:
    def __init__(
        self,
        master:tk.Misc,
        column:int,
        row:int,
        columnspan:int = 1,
        sticky:str = NSEW,
    ) -> None:
        grid = GridUtil(column, row, columnspan, sticky)

        self.master = master

        self.lock = th.Lock()

        self.image:ImageTk.PhotoImage = None
        self.image_cylcle:cycle = None
        self.duration:int = 33

        self.view = ttk.Label(master)
        self.view.grid(column=grid.column, row=grid.row, columnspan=grid.columnspan, sticky=grid.sticky)

        self.update_image()

    def set_images(self, images:list[Image.Image], duration:float) -> None:
        """[Thread-N] ビューに使用する画像をセット

        Args:
            images (list[Image.Image]): 画像リスト
            duration (float): 画像1枚あたりの表示時間(ミリ秒)
        """
        with self.lock:
            self.image_cylcle = cycle([ImageTk.PhotoImage(image) for image in images])
            self.duration = int(duration)

    def update_image(self) -> None:
        """[MainThread] ビューの画像を更新
        """
        if self.image_cylcle is None:
            self.master.after(33, self.update_image)
        elif not self.lock.acquire(True, 0.0):
            # NOTE: メインスレッドでロック取得待機するとメインスレッドが止まるので流します。
            self.master.after(33, self.update_image)
        else:
            self.image:ImageTk.PhotoImage = next(self.image_cylcle)

            self.lock.release()

            self.view.configure(image=self.image)
            self.master.after(self.duration, self.update_image)
