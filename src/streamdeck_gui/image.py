from abc import ABC, abstractmethod
from PIL import Image as PILImage
from io import BytesIO

class Image(ABC):
    @abstractmethod
    def get(self) -> bytes: raise NotImplementedError

class PillowImage(Image, ABC):
    def __init__(self, image: PILImage.Image, resize: bool = False) -> None:
        if image.size != self.size: 
            if resize: image = image.resize(self.size)
            else: raise ValueError("incorrect image size")
        img_bytes = BytesIO()
        image.convert("RGB").save(img_bytes, format='JPEG')
        self._data = img_bytes.getvalue()

    def get(self) -> bytes: return self._data

    @classmethod
    def from_file(cls, filepath: str, resize: bool = True):
        return cls(PILImage.open(filepath), resize)

    @property
    @staticmethod
    @abstractmethod
    def size() -> tuple[int, int]: raise NotImplementedError
        
class TouchscreenImage(PillowImage):
    size = (800, 100)

class ButtonImage(PillowImage):
    size = (120, 120)
