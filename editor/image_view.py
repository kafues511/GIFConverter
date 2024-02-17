import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import threading as th
from PIL import Image, ImageTk
from itertools import cycle


__all__ = [
    "ImageView",
]


class ImageView:
    def __init__(
        self,
        master:tk.Misc,
        column:int,
        row:int,
    ) -> None:
        self.master = master

        self.lock = th.Lock()

        self.item_id:int = None
        self.image:ImageTk.PhotoImage = None
        self.image_cylcle:cycle = None
        self.duration:int = 33

        self.canvas = ttk.Canvas(master)
        self.canvas.grid(column=column, row=row, sticky=NSEW)

        self.yview = ttk.Scrollbar(master, orient=VERTICAL, command=self.canvas.yview)
        self.yview.grid(column=column+1, row=row, sticky=NS)

        self.xview = ttk.Scrollbar(master, orient=HORIZONTAL, command=self.canvas.xview)
        self.xview.grid(column=column, row=row+1, sticky=EW)

        self.canvas.configure(xscrollcommand=self.xview.set, yscrollcommand=self.yview.set)

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

            if self.item_id is None:
                self.item_id = self.canvas.create_image(0, 0, anchor=NW, image=self.image)
            else:
                self.canvas.itemconfig(self.item_id, image=self.image)

            self.canvas.configure(width=self.image.width(), height=self.image.height(), scrollregion=(0, 0, self.image.width(), self.image.height()))
            self.master.after(self.duration, self.update_image)
