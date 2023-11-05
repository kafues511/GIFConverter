import cv2
import numpy as np
from PIL import Image
from typing import Union, Optional
from pathlib import Path


def image_quantize(
    image:np.ndarray,
    colors:int=256,
    method:int=Image.Quantize.MEDIANCUT,
    dither:int=Image.Dither.NONE,
    mode:str="RGB",
) -> Image.Image:
    """画像の量子化

    Args:
        image (np.ndarray): 入力画像(RGB配置を想定)
        colors (int, optional): 減色後の色数. Defaults to 256.
        method (int, optional): 量子化の種類. Defaults to Image.Quantize.MEDIANCUT.
        dither (int, optional): ディザの種類. Defaults to Image.Dither.NONE.
        mode (str, optional): 出力結果の形式. Defaults to "RGB".

    Returns:
        Image.Image: 量子化された画像
    """
    image:Image.Image = Image.fromarray(image, mode=mode)
    image = image.quantize(colors=colors, method=method, dither=dither)
    return image.convert(mode)


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


def simple_sample(filename:Union[str, Path]) -> None:
    """サンプル

    Args:
        filename (Union[str, Path]): 動画の入力パス
    """
    if isinstance(filename, str):
        filename:Path = Path(filename)

    # *.mp4以外の入力をする予定がない
    if filename.suffix != ".mp4":
        return None

    # read errorはwithで無視されちゃうのでここで止めておく
    if not filename.is_file():
        return None

    input_path = filename
    output_path = filename.with_suffix(".gif")

    with WithVideoCapture(str(input_path)) as cap:
        images:list[Image.Image] = []

        # apply scale.
        width = cap.width - cap.width//2
        height = cap.height - cap.height//2

        while cap.read():
            image = cap.image
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            image = image_quantize(image, method=Image.Quantize.MEDIANCUT)
            images.append(image)

    # 読込欠損発生
    if len(images) != cap.frames:
        return None

    images[0].save(str(output_path), save_all=True, append_images=images[1:], optimize=False, duration=1.0 / cap.fps * 1000.0, loop=0)


if __name__ == "__main__":
    simple_sample(r"F:\GIFConverter\sample\41.mp4")
