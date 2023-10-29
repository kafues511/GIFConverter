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


class CustomVideoCapture(cv2.VideoCapture):
    def __enter__(self) -> "CustomVideoCapture":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.release()
        except Exception:
            pass

    @property
    def retval(self) -> bool:
        """最後にread()した結果を取得します。

        Returns:
            bool: 最後にread()した結果
        """
        try:
            return self.__retval
        except Exception:
            return False

    @property
    def image(self) -> Optional[np.ndarray]:
        """最後にread()で読み込んだ画像を取得します。

        Returns:
            Optional[np.ndarray]: 最後にread()で取得した画像データ
        """
        try:
            return self.__image
        except Exception:
            return None

    def read(self) -> bool:
        """cv2.VideoCapture.read()と同様

        Returns:
            bool: cv2.VideoCapture.read()の結果
        """
        self.__retval, self.__image = super().read()
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

    with CustomVideoCapture(str(input_path)) as cap:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        images:list[Image.Image] = []

        # apply scale.
        width = width - width//2
        height = height - height//2

        while cap.read():
            image = cap.image
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            image = image_quantize(image, method=Image.Quantize.MEDIANCUT)
            images.append(image)

    # 読込欠損発生
    if len(images) != frames:
        return None

    images[0].save(str(output_path), save_all=True, append_images=images[1:], optimize=False, duration=1.0 / fps * 1000.0, loop=0)


if __name__ == "__main__":
    simple_sample(r"F:\GIFConverter\sample\41.mp4")
