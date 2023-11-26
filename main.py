import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from pathlib import Path
from typing import Optional, Callable
from PIL import Image

from editor import *
from editor.grid_util import *
from runtime.gif_converter import GIFConverter


class RowCounter:
    """行数カウンタ
    """
    def __init__(self) -> None:
        self.row = 0

    def __call__(self, is_readonly:bool=False) -> int:
        """現在の行数を取得します。

        取得するたびに行数がカウントされます。

        Args:
            is_readonly (bool, optional): カウントしない場合はTrueを指定します。. Defaults to False.

        Returns:
            int: 現在の行数
        """
        ret = self.row
        if not is_readonly:
            self.row += 1
        return ret


class GIFConverterControlFrame(ttk.Frame):
    def __init__(
        self,
        master:tk.Misc,
        callback_gif_export:Optional[Callable[[], None]] = None,
        callback_export_ready:Optional[Callable[[], bool]] = None,
    ) -> None:
        super().__init__(master, relief=RAISED, padding=10)

        row = RowCounter()

        self.input_video_file = InputVideoFile(self, column=(0, 0, 1), row=row(), columnspan=(1, 2, 1), callback_path_update=self.update_input_path)
        self.quantize_method = QuantizeMethod(self, column=0, row=row(), columnspan=(1, 1, 1))
        self.quantize_kmeans = QuantizeKMeans(self, column=0, row=row(), columnspan=(1, 2, 1))
        self.image_resize = ImageResize(self, column=(0, 0), row=row(), columnspan=(1, 2))
        self.play_speed = PlaySpeed(self, column=(0, 0), row=row(), columnspan=(1, 2))
        self.output_gif_file = OutputGifFile(self, column=(0, 0, 1), row=row(), columnspan=(1, 2, 1))
        self.export_file_size = ExportFileSize(self, column=0, row=row(), columnspan=(1, 2))
        self.export_state = ExportState(self, column=(0, 0, 1), row=row(), columnspan=(1, 2, 1), callback_export=callback_gif_export)

        # register callback.
        self.callback_export_ready = callback_export_ready

        self.grid_columnconfigure([i for i in range(4)], weight=1)
        self.grid_rowconfigure([i for i in range(row(True))], weight=1)

    def update_input_path(self, input_path:str) -> None:
        """入力パスの更新

        Args:
            input_path (str): 新しい入力パス
        """
        if GIFConverter.is_valid_path(input_path, True, GIFConverter.SUPPORT_SUFFIXES):
            state = SUCCESS
        else:
            state = DISABLED

        if self.callback_export_ready is not None and not self.callback_export_ready():
            state = DISABLED

        self.export_state.set_button_state(state)


class GIFPreviewFrame(ttk.Frame):
    def __init__(self, master:tk.Misc) -> None:
        super().__init__(master, relief=RAISED, padding=10)

        self.image_view = ImageView(self, column=0, row=0, columnspan=1, sticky=NSEW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


class GIFConverterEditor(ttk.Window):
    def __init__(self) -> None:
        super().__init__("GIFConverter", minsize=(640, 278))

        # GIFConverter
        self.gif_converter = GIFConverter()

        # 操作パネル
        self.control_frame = GIFConverterControlFrame(self, self.gif_export, lambda: self.gif_converter.is_thread_ready())
        self.control_frame.grid(column=0, row=0, padx=10, pady=10, sticky=NSEW)

        # GIFプレビュー
        self.preview_frame = GIFPreviewFrame(self)
        self.preview_frame.grid(column=0, row=1, padx=10, pady=(0, 10), sticky=NSEW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    @property
    def input_path(self) -> Optional[Path]:
        """入力パスを取得

        Returns:
            Optional[Path]: 入力パスが存在しない場合はNoneを返します。
        """
        if (path:=self.control_frame.input_video_file.path) == "":
            return None

        if not (path:=Path(path)).is_file():
            return None

        if path.suffix not in GIFConverter.SUPPORT_SUFFIXES:
            return None

        return path

    @property
    def image_resize(self) -> float:
        """画像のリサイズを取得

        Returns:
            float: 画像のリサイズ
        """
        return self.control_frame.image_resize.image_resize

    @property
    def quantize_method(self) -> int:
        """量子化の種類を取得

        Returns:
            int: 量子化の種類
        """
        return self.control_frame.quantize_method.quantize_method

    @property
    def quantize_kmeans(self) -> int:
        """クラスタ数を取得

        Returns:
            int: クラスタ数
        """
        return self.control_frame.quantize_kmeans.kmeans

    @property
    def play_speed(self) -> float:
        """再生速度を取得

        Returns:
            float: 再生速度
        """
        return self.control_frame.play_speed.play_speed

    def get_output_path(self, input_path:Optional[Path]) -> Optional[Path]:
        """出力先を取得

        Args:
            input_path (Optional[Path]): 入力パス

        Returns:
            Optional[Path]: 出力先が存在しない場合はNoneを返します。
        """
        # 出力先が指定されている場合
        if (path:=self.control_frame.output_gif_file.path) != "":
            # ディレクトリが指定されている場合.
            if (path:=Path(path)).suffix == "":
                # 無効なディレクトリ.
                if not path.is_dir():
                    return None

                # ディレクトリ指定の場合は入力パスが必要.
                if input_path is None:
                    return None

                # 入力パスのファイル名を結合.
                return path / f"{input_path.stem}.gif"

            # パスが指定されていて且つ有効な拡張子.
            elif path.suffix == ".gif":
                return path

            # パスが指定されていて且つ無効な拡張子.
            else:
                return None

        # 出力先が指定されていない、且つ入力パスが指定されていない場合.
        if (path:=self.input_path) is None:
            return None

        # 入力パスの拡張子を置換
        return path.with_suffix(".gif")

    def set_preview_images(self, images:list[Image.Image], duration:float) -> None:
        """GIFプレビューの画像をセット

        表示時間はintに切り上げられます。

        Args:
            images (list[Image.Image]): 画像
            duration (float): 1枚あたりの表示時間(ミリ秒)
        """
        self.preview_frame.image_view.set_images(images, duration)

    @staticmethod
    def get_display_name_file_size(st_size:int) -> str:
        """ファイルサイズを表示名で取得します。

        Args:
            st_size (int): ファイルサイズ

        Returns:
            str: 未対応の単位や不正なファイルサイズを入力した場合は Unknown と表示されます。
        """
        try:
            for unit in ["Byte", "KB", "MB", "GB", "TB"]:
                if st_size < 1024.0:
                    return f"{st_size:.2f} {unit}"
                st_size /= 1024.0
        except Exception as e:
            pass

        return "Unknown"

    def update_export_state(self, is_success:bool, output_path:str) -> None:
        """Export状態の更新

        Args:
            is_success (bool): 出力結果の成否
            output_path (str): 出力先のパス
        """
        self.control_frame.export_state.end(is_success)
        if is_success:
            st_size = Path(output_path).stat().st_size
            self.control_frame.export_file_size.filesize_var.set(self.get_display_name_file_size(st_size))
        else:
            self.control_frame.export_file_size.filesize_var.set("nan")

    def gif_export(self) -> None:
        """GIF作成
        """
        if (input_path:=self.input_path) is None:
            return

        if (output_path:=self.get_output_path(input_path)) is None:
            return

        ret = self.gif_converter.export(
            input_path,
            output_path,
            self.image_resize,
            self.quantize_method,
            self.quantize_kmeans,
            self.play_speed,
            8,
            self.set_preview_images,
            self.update_export_state,
        )

        if ret:
            self.control_frame.export_state.start()


if __name__ == "__main__":
    app = GIFConverterEditor()
    app.mainloop()
