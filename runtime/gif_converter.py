from pathlib import Path
import multiprocessing as mp
import threading as th
from typing import Union, Optional, Callable, Any
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass


__all__ = [
    "WithVideoCapture",
    "GIFConverter",
]


class WithVideoCapture:
    """with対応なcv2.VideoCapture
    """
    def __init__(self, filename:str) -> None:
        """コンストラクタ

        Args:
            filename (str): 動画のファイルパス
        """
        self.cap = cv2.VideoCapture(filename)

    def __enter__(self) -> "WithVideoCapture":
        # NOTE: 一部プロパティはreadし終えてから読み込むと0.0になります。
        self.__width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.__height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.__fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.__frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.__frame = -1
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.cap.release()

    @property
    def width(self) -> int:
        """画像の横幅を取得

        Returns:
            int: 画像の横幅
        """
        return self.__width

    @property
    def height(self) -> int:
        """画像の縦幅を取得

        Returns:
            int: 画像の縦幅
        """
        return self.__height

    @property
    def fps(self) -> float:
        """フレームレートを取得

        Returns:
            float: フレームレート
        """
        return self.__fps

    @property
    def frames(self) -> int:
        """総フレーム数を取得

        Returns:
            int: 総フレーム数
        """
        return self.__frames

    @property
    def retval(self) -> bool:
        """最後のread結果を取得

        Returns:
            bool: 読込に成功した場合はTrueを返します。
        """
        try:
            return self.__retval
        except Exception:
            return False

    @property
    def image(self) -> Optional[np.ndarray]:
        """最後のreadで読み込んだ画像を取得

        Returns:
            Optional[np.ndarray]: 読み込みに成功した場合は画像データを返します。
        """
        try:
            return self.__image
        except Exception:
            return None

    @property
    def frame(self) -> int:
        """現在のフレーム数を取得

        readするたびに進みます。

        Returns:
            int: 現在のフレーム数、又は一度もreadしていない場合は-1を返します。
        """
        try:
            return self.__frame
        except Exception:
            return -1

    def read(self) -> bool:
        """読込

        Returns:
            bool: 読込結果
        """
        self.__retval, self.__image = self.cap.read()
        self.__frame += 1
        return self.retval


@dataclass
class GIFExportInfo:
    """GIF変換、出力情報
    """
    input_path:str
    output_path:str
    resize:float
    quantize_method:int
    quantize_kmeans:int
    play_speed:float
    num_workers:int

    def __post_init__(self) -> None:
        if isinstance(self.input_path, Path):
            self.input_path = str(self.input_path)

        if isinstance(self.output_path, Path):
            self.output_path = str(self.output_path)

        self.num_workers = max(1, self.num_workers)


class GIFConverter:
    """GIF変換と出力
    """
    # GIF変換可能な拡張子
    SUPPORT_SUFFIXES = tuple([".mp4", ".avi"])

    def __init__(self) -> None:
        """コンストラクタ
        """
        # GIF変換と出力を行うスレッド
        self.thread:th.Thread = None

    @staticmethod
    def is_valid_path(in_path:Any, is_file:bool, suffix:Optional[Union[str, tuple[str, ...]]]) -> bool:
        """パスの有効性チェック

        Args:
            in_path (Any): チェックするパス
            is_file (bool): ファイルが存在するか確認します。
            suffix (Optional[Union[str, tuple[str, ...]]]): 拡張子を限定する場合に指定します。

        Returns:
            bool: _description_
        """
        if isinstance(in_path, str) and in_path != "":
            in_path:Path = Path(in_path)
        elif not isinstance(in_path, Path):
            return False

        # ファイルの有無が指定されている場合.
        if is_file and not in_path.is_file():
            return False

        # 拡張子が指定されている場合は含まれるか.
        if suffix is not None and in_path.suffix not in suffix:
            return False

        return True

    def is_thread_ready(self) -> bool:
        """スレッドの立ち上げ準備が整っているかを取得します。

        Returns:
            bool: スレッドを立ち上げられる場合はTrueを返します。
        """
        if self.thread is None:
            return True

        # スレッドが生きている場合は準備完了していません。
        return not self.thread.is_alive()

    def export(
        self,
        input_path:Union[Path, str],
        output_path:Union[Path, str],
        resize:float,
        quantize_method:int,
        quantize_kmenas:int,
        play_speed:float,
        num_workers:int,
        quantized_callback:Optional[Callable[[list[Image.Image], float], None]] = None,
        exported_callback:Optional[Callable[[bool, str], None]] = None,
    ) -> bool:
        """[MainThread] GIF変換と出力

        Args:
            input_path (Union[Path, str]): 動画の入力パス
            output_path (Union[Path, str]): GIFの出力パス
            resize (float): リサイズ
            quantize_method (int): 量子化の種類
            quantize_kmeans (int): クラスタ数
            play_speed (float): 再生速度
            num_workers (int): 量子化処理のワーカー数
            quantized_callback (Optional[Callable[[list[Image.Image], float], None]], optional): 量子化後のコールバック. Defaults to None.
            exported_callback (Optional[Callable[[bool, str], None]], optional): GIF出力後のコールバック. Defaults to None.

        Returns:
            bool: スレッドの立ち上げに成功した場合はTrueを返します。
        """
        # 最後に実行したGIF変換が完了しているか
        if not self.is_thread_ready():
            return False

        # 入力先の有効性を確認
        if not GIFConverter.is_valid_path(input_path, True, self.SUPPORT_SUFFIXES):
            return False

        # 出力先の有効性を確認
        if not GIFConverter.is_valid_path(output_path, False, ".gif"):
            return False

        # GIF変換スレッドの立ち上げ
        self.thread = th.Thread(
            target=self.thread_export,
            args=(
                GIFExportInfo(
                    input_path,
                    output_path,
                    resize,
                    quantize_method,
                    quantize_kmenas,
                    play_speed,
                    num_workers,
                ),
                quantized_callback,
                exported_callback,
            ),
            daemon=True,
        )
        self.thread.start()

        return True

    def thread_export(
        self,
        info:GIFExportInfo,
        quantized_callback:Optional[Callable[[list[Image.Image], float], None]] = None,
        exported_callback:Optional[Callable[[bool, str], None]] = None,
    ) -> None:
        """[Thread-N] GIF変換と出力

        Args:
            info (GIFExportInfo): GIF変換、出力情報
            quantized_callback (Optional[Callable[[list[Image.Image], float], None]], optional): 量子化後のコールバック. Defaults to None.
            exported_callback (Optional[Callable[[bool, str], None]], optional): GIF出力後のコールバック. Defaults to None.
        """
        # 量子化スレッドの入出力用
        input_queue = mp.Queue()
        output_queue = mp.Queue()

        # 量子化スレッドリスト
        # NOTE: 元はプロセスだけどtkinterとの相性問題でスレッドに変更.
        threads:list[th.Thread] = []

        # 動画読込
        with WithVideoCapture(info.input_path) as cap:
            # プロセスの立ち上げ
            for _ in range(info.num_workers):
                if info.resize != 1.0:
                    thread = th.Thread(
                        target=GIFConverter.update_image_scale_quantize,
                        args=(
                            input_queue,
                            output_queue,
                            int(cap.width * info.resize),
                            int(cap.height * info.resize),
                            cv2.INTER_AREA,
                            info.quantize_method,
                            info.quantize_kmeans,
                        ),
                        daemon=True,
                    )
                else:
                    thread = th.Thread(
                        target=GIFConverter.update_image_quantize,
                        args=(
                            input_queue,
                            output_queue,
                            info.quantize_method,
                            info.quantize_kmeans,
                        ),
                        daemon=True,
                    )
                thread.start()
                threads.append(thread)

            # 画像をキューに突っ込む
            while cap.read():
                input_queue.put((cap.frame, cv2.cvtColor(cap.image, cv2.COLOR_BGRA2RGB)))

        # 量子化スレッドの終了合図を送信
        for _ in range(info.num_workers):
            input_queue.put(None)

        try:
            # 画像をフレーム順に並び替え
            images:list[tuple[int, Image.Image]] = [output_queue.get() for _ in range(cap.frames)]
            images:list[Image.Image] = [image for _, image in sorted(images, key=lambda values: values[0])]

            # 画像1枚あたりの表示時間
            duration = 1.0 / (cap.fps * info.play_speed) * 1000.0

            # 量子化完了後のコールバックが登録されている場合は、画像と表示時間を渡します。
            if quantized_callback is not None:
                quantized_callback(images, duration)

            # GIF出力
            images[0].save(info.output_path, save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)

            # 出力結果
            is_success = True
        except Exception:
            is_success = False

        # GIF出力後のコールバックが登録されている場合は、成否を渡します。
        if exported_callback is not None:
            exported_callback(is_success, info.output_path)

    @staticmethod
    def update_image_scale_quantize(
        input_queue:mp.Queue,
        output_queue:mp.Queue,
        width:int,
        height:int,
        interpolation:int,
        quantize_method:int,
        quantize_kmeans:int,
    ) -> None:
        """画像のリサイズと量子化

        処理された画像は出力キューに積まれます。

        Args:
            input_queue (mp.Queue): 画像の入力キュー
            output_queue (mp.Queue): 画像の出力キュー
            width (int): リサイズ後の横幅
            height (int): リサイズ後の縦幅
            interpolation (int): リサイズの補間方法
            quantize_method (int): 量子化の種類
            quantize_kmeans (int): クラスタ数
        """
        while True:
            # Noneを受け取るまで仕事をします.
            if (values:=input_queue.get()) is None:
                return

            # リサイズ後に量子化を行います.
            frame, image = values
            image = cv2.resize(image, (width, height), interpolation=interpolation)
            image = GIFConverter.image_quantize(image, method=quantize_method, kmeans=quantize_kmeans)

            # 加工結果を送信します.
            output_queue.put((frame, image))

    @staticmethod
    def update_image_quantize(
        input_queue:mp.Queue,
        output_queue:mp.Queue,
        quantize_method:int,
        quantize_kmeans:int,
    ) -> None:
        """画像の量子化

        Args:
            input_queue (mp.Queue): 画像の入力キュー
            output_queue (mp.Queue): 画像の出力キュー
            quantize_method (int): 量子化の種類
            quantize_kmeans (int): クラスタ数
        """
        while True:
            # Noneを受け取るまで仕事をします。
            if (values:=input_queue.get()) is None:
                return

            # 量子化を行います。
            frame, image = values
            image = GIFConverter.image_quantize(image, method=quantize_method, kmeans=quantize_kmeans)

            # 加工結果を送信します。
            output_queue.put((frame, image))

    @staticmethod
    def image_quantize(
        image:np.ndarray,
        colors:int=256,
        method:int=Image.Quantize.MEDIANCUT,
        kmeans:int=0,
        dither:int=Image.Dither.NONE,
        mode:str="RGB",
    ) -> Image.Image:
        """画像の量子化

        Args:
            image (np.ndarray): 入力画像(RGB配置を想定)
            colors (int, optional): 減色後の色数. Defaults to 256.
            method (int, optional): 量子化の種類. Defaults to Image.Quantize.MEDIANCUT.
            kmeans (int, optional): クラスタ数. Defaults to 0.
            dither (int, optional): ディザの種類. Defaults to Image.Dither.NONE.
            mode (str, optional): 出力結果の形式. Defaults to "RGB".

        Returns:
            Image.Image: 量子化された画像
        """
        image:Image.Image = Image.fromarray(image, mode=mode)
        if method != -1:
            image = image.quantize(colors=colors, method=method, kmeans=kmeans, dither=dither)
        return image.convert(mode)
