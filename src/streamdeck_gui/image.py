from abc import ABC, abstractmethod
from PIL import Image as PILImage
from io import BytesIO

class Image(ABC):
    @abstractmethod
    def get(self) -> bytes: raise NotImplementedError

class PillowImage(Image):
    def __init__(self, image: PILImage.Image) -> None:
        img_bytes = BytesIO()
        image.convert("RGB").save(img_bytes, format='JPEG')
        self._data = img_bytes.getvalue()

    def get(self) -> bytes: return self._data

    @classmethod
    def from_file(cls, filepath: str):
        return cls(PILImage.open(filepath))
