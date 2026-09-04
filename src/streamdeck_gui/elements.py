from abc import ABC, abstractmethod
from typing import Optional, List
from StreamDeck.DeviceManager import StreamDeck
from PIL import Image as PILImage

from .image import Image, PillowImage
from .events import TouchscreenEvent, ButtonEvent, DialPushEvent, DialTurnEvent, PressEvent

class Element:
    def __init__(self) -> None:
        self._parent: Optional[Element] = None
        self._root: Optional[RootElement] = None

    def _attach(self, parent: Element, root: RootElement) -> None:
        self._parent = parent
        self._root = root

    def set_visible(self) -> None: pass
    def set_hidden(self) -> None: pass

class RootElement(Element):
    def __init__(self, deck: StreamDeck) -> None:
        super().__init__()
        self._attach(self, self)
        self._deck = deck
        self._button_section: Optional[ButtonSection] = None
        self._touchscreen: Optional[Touchscreen] = None
        self._dial_section: Optional[DialSection] = None

    def get_btns(self) -> Optional[ButtonSection]:
        return self._button_section

    def set_btns(self, btn_section: ButtonSection) -> None:
        if self._button_section is not None: self._button_section.set_hidden()
        self._button_section = btn_section
        btn_section._attach(self, self)
        btn_section.set_visible()

    def get_touchscreen(self) -> Optional[Touchscreen]:
        return self._touchscreen

    def set_touchscreen(self, touchscreen: Touchscreen) -> None:
        if self._touchscreen is not None: self._touchscreen.set_hidden()
        self._touchscreen = touchscreen
        touchscreen._attach(self, self)
        touchscreen.set_visible()

    def get_dials(self) -> Optional[DialSection]:
        return self._dial_section

    def set_dials(self, dial_section: DialSection) -> None:
        if self._dial_section is not None: self._dial_section.set_hidden()
        self._dial_section = dial_section
        dial_section._attach(self, self)
        dial_section.set_visible()

    def btn_update(self, event: ButtonEvent) -> None:
        if self._button_section is not None:
            self._button_section.press_update(event)

    def set_button_image(self, btn_idx: int, image: Optional[Image]) -> None:
        self._deck.set_key_image(btn_idx, image.get() if image is not None else None)

    def touch_update(self, event: TouchscreenEvent) -> None:
        if self._touchscreen is not None:
            self._touchscreen.update(event)

    def set_touchscreen_image(self, image: Optional[Image], x_pos: int = 0, y_pos: int = 0, width: int = 800, height: int = 100) -> None:
        self._deck.set_touchscreen_image(image.get() if image is not None else None, x_pos, y_pos, width, height)

    def dial_push_update(self, event: DialPushEvent) -> None:
        if self._dial_section is not None:
            self._dial_section.press_update(event)

    def dial_turn(self, event: DialTurnEvent) -> None:
        if self._dial_section is not None:
            self._dial_section.turn(event)

class Pressable(ABC):
    @abstractmethod
    def down(self) -> None: raise NotImplementedError

    @abstractmethod
    def up(self) -> None: raise NotImplementedError

class OneOfElement(Element):
    def __init__(self):
        super().__init__()
        self._idx: Optional[int] = None

    def _attach(self, parent: Element, root: RootElement, idx: int):
        super()._attach(parent, root)
        self._idx = idx

class Drawable(ABC):
    @abstractmethod
    def _draw_image(self, image: Optional[Image]) -> None: raise NotImplementedError

class Button(OneOfElement, Pressable, Drawable):
    def _draw_image(self, image: Optional[Image]) -> None:
        assert self._idx is not None
        self._root.set_button_image(self._idx, image)

    def down(self) -> None: pass
    def up(self) -> None: pass

class Section[T: OneOfElement](Element):
    def __init__(self, items: Optional[List[Optional[T]]]) -> None:
        super().__init__()
        self._items: List[Optional[T]] = items or [None] * 8

    def _attach(self, parent, root):
        super()._attach(parent, root)
        for i, item in enumerate(self._items):
            if item is not None: item._attach(parent, root, i)

    def set_visible(self) -> None:
        super().set_visible()
        for item in self._items:
            if item is not None: item.set_visible()

    def set_hidden(self) -> None:
        super().set_hidden()
        for item in self._items:
            if item is not None: item.set_hidden()

class PressableSection[T: Pressable](Section[T]):
    def press_update(self, event: PressEvent) -> None:
        if (btn := self._items[event.idx]) is not None:
            if event.pressed: btn.down()
            else: btn.up()

class ButtonSection(PressableSection[Button]): pass

class Touchscreen(Element, Drawable):
    def _draw_image(self, image: Optional[Image], x_pos: int = 0, y_pos: int = 0, width: int = 800, height: int = 100) -> None:
        self._root.set_touchscreen_image(image, x_pos, y_pos, width, height)

class Dial(OneOfElement, Pressable):
    def turn(value: int) -> None: pass

class DialSection(PressableSection[Dial]):
    def turn(self, event: DialTurnEvent) -> None:
        if (dial := self._items[event.idx]) is not None:
            dial.turn(event.value)

class ButtonImage(PillowImage):
    def __init__(self, image: PILImage.Image) -> None:
        super().__init__(image.resize((120, 120)))

class StaticImage(Element, Drawable, ABC):
    IMAGE: Optional[Image] = None

    def set_visible(self) -> None:
        super().set_visible()
        self._draw_image(self.IMAGE)

class StaticButton(StaticImage, Button): pass

class VisibilityAwareButton(Button):
    def __init__(self):
        super().__init__()
        self._visible = False

    def set_visible(self):
        super().set_visible()
        self._visible = True

    def set_hidden(self):
        super().set_hidden()
        self._visible = False
        
class TouchscreenImage(PillowImage):
    def __init__(self, image: PILImage.Image) -> None:
        super().__init__(image.resize((800, 100)))

class StaticTouchscreen(StaticImage, Touchscreen): pass
