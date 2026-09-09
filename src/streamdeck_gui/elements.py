from abc import ABC, abstractmethod
from typing import Optional, List
from itertools import repeat, chain, islice
from StreamDeck.DeviceManager import StreamDeck
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

from .image import Image
from .events import TouchscreenEvent, TouchscreenEventShort, TouchscreenEventLong, TouchscreenEventDrag, ButtonEvent, DialPushEvent, DialTurnEvent, PressEvent
from .hierarchy import HierarchyElement

class Element(HierarchyElement["Element", "RootElement"]):
    def detach(self):
        self.set_hidden()
        super().detach()

    def set_visible(self) -> None: pass
    def set_hidden(self) -> None: pass

class RootElement(Element):
    def __init__(self, deck: StreamDeck) -> None:
        super().__init__()
        self.attach(self, self)
        deck.set_key_callback(lambda _, key, key_state: self._btn_update(ButtonEvent(key, key_state)))
        deck.set_dial_callback(self._dial_change_callback)
        deck.set_touchscreen_callback(self._touchscreen_event_callback)
        self._deck = deck
        self._button_section: Optional[ButtonSection] = None
        self._touchscreen: Optional[Touchscreen] = None
        self._dial_section: Optional[DialSection] = None
        self._down_buttons: dict[int, DialSection] = {}

    def _dial_change_callback(self, _, dial, event, value):
        if event == DialEventType.PUSH:
            self._dial_push_update(DialPushEvent(dial, value))
        elif event == DialEventType.TURN:
            self._dial_turn(DialTurnEvent(dial, value))

    def _touchscreen_event_callback(self, _, evt_type, value):
        x, y = value["x"], value["y"]
        if evt_type == TouchscreenEventType.SHORT:
            event = TouchscreenEventShort(x, y)

        elif evt_type == TouchscreenEventType.LONG:
            event = TouchscreenEventLong(x, y)

        elif evt_type == TouchscreenEventType.DRAG:
            x_out, y_out = value["x_out"], value["y_out"]
            event = TouchscreenEventDrag(x, y, x_out, y_out)

        self._touch_update(event)

    def set_sections(self, btn_section: Optional[ButtonSection], touchscreen: Optional[Touchscreen], dial_section: Optional[DialSection]):
        if btn_section is not self._button_section:
            self._detach_section(self._button_section)
            self._button_section = btn_section
            self._attach_section(btn_section)

        if touchscreen is not self._touchscreen:
            self._detach_section(self._touchscreen)
            self._touchscreen = touchscreen
            self._attach_section(touchscreen)

        if dial_section is not self._dial_section:
            self._detach_section(self._dial_section)
            self._dial_section = dial_section
            self._attach_section(dial_section)

    @staticmethod
    def _detach_section(section: Optional[Section]):
        if section is not None: section.detach()

    def _attach_section(self, section: Optional[Section]):
        if section is None: return
        section.attach(self, self)
        section.set_visible()

    def get_btns(self) -> Optional[ButtonSection]:
        return self._button_section

    def get_touchscreen(self) -> Optional[Touchscreen]:
        return self._touchscreen

    def get_dials(self) -> Optional[DialSection]:
        return self._dial_section

    def _btn_update(self, event: ButtonEvent) -> None:
        if not event.pressed:
            if (section := self._down_buttons.pop(event.idx)) is not None:
                section.press_update(event)
            return
        
        if self._button_section is not None:
            self._down_buttons[event.idx] = self._button_section
            self._button_section.press_update(event)

    def set_button_image(self, btn_idx: int, image: Optional[Image]) -> None:
        self._deck.set_key_image(btn_idx, image.get() if image is not None else None)

    def _touch_update(self, event: TouchscreenEvent) -> None:
        if self._touchscreen is not None:
            self._touchscreen.update(event)

    def set_touchscreen_image(self, image: Optional[Image], x_pos: int = 0, y_pos: int = 0, width: int = 800, height: int = 100) -> None:
        self._deck.set_touchscreen_image(image.get() if image is not None else None, x_pos, y_pos, width, height)

    def _dial_push_update(self, event: DialPushEvent) -> None:
        if self._dial_section is not None:
            self._dial_section.press_update(event)

    def _dial_turn(self, event: DialTurnEvent) -> None:
        if self._dial_section is not None:
            self._dial_section.turn(event)

class VisibilityAware(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._visible = False

    def set_visible(self):
        super().set_visible()
        self._visible = True

    def set_hidden(self):
        super().set_hidden()
        self._visible = False

class Pressable(ABC):
    @abstractmethod
    def down(self) -> None: raise NotImplementedError

    @abstractmethod
    def up(self) -> None: raise NotImplementedError

class OneOfElement(Element):
    def __init__(self):
        super().__init__()
        self._idx: Optional[int] = None

    def attach(self, parent: Element, root: RootElement, idx: int):
        super().attach(parent, root)
        self._idx = idx

    def detach(self):
        super().detach()
        self._idx = None

class Drawable(ABC):
    @abstractmethod
    def draw_image(self, image: Optional[Image]) -> None: raise NotImplementedError

class Button(OneOfElement, Pressable, Drawable):
    def draw_image(self, image: Optional[Image]) -> None:
        assert self._idx is not None
        self.root.set_button_image(self._idx, image)

    def down(self) -> None: pass
    def up(self) -> None: pass

class Section[T: OneOfElement](VisibilityAware, Element):
    def __init__(self, *items: Optional[T]) -> None:
        super().__init__()
        self._items: List[Optional[T]] = list(self._pad(*items)) # pad items with None to size 8

    @staticmethod
    def _pad(*items: Optional[T]) -> islice[Optional[T]]:
        return islice(chain(items, repeat(None)), 8)

    def attach(self, parent, root):
        super().attach(parent, root)
        for i, item in enumerate(self._items):
            if item is not None: item.attach(self, root, i)

    def detach(self):
        super().detach()
        for item in self._items:
            if item is not None: item.detach()

    def set_visible(self) -> None:
        super().set_visible()
        for item in self._items:
            if item is not None: item.set_visible()

    def set_hidden(self) -> None:
        super().set_hidden()
        for item in self._items:
            if item is not None: item.set_hidden()

    def remove(self, idx: int) -> Optional[T]:
        item = self._items[idx]
        if item is None: return None
        item.detach()
        self._items[idx] = None
        return item

    def _attach(self, idx: int, item: Optional[T]):
        self._items[idx] = item
        item.attach(self, self.root, idx)
        if self._visible: item.set_visible()


    def set(self, idx: int, item: Optional[T]) -> Optional[T]:
        if self._items[idx] is item: return
        prev = self.remove(idx)
        if item is None: return
        self._attach(idx, item)
        return prev

    def update(self, *items: Optional[T]):
        for i, item in enumerate(self._pad(*items)):
            if item is self._items[i]: continue
            self.remove(i)

        for i, item in enumerate(self._pad(*items)):
            if item is self._items[i]: continue
            self._attach(i, item)

class PressableSection[T: Pressable](Section[T]):
    def press_update(self, event: PressEvent) -> None:
        if (btn := self._items[event.idx]) is not None:
            if event.pressed: btn.down()
            else: btn.up()

class ButtonSection(PressableSection[Button]): pass

class Touchscreen(Element, Drawable):
    def update(self, event: TouchscreenEvent) -> None: pass

    def draw_image(self, image: Optional[Image], x_pos: int = 0, y_pos: int = 0, width: int = 800, height: int = 100) -> None:
        self.root.set_touchscreen_image(image, x_pos, y_pos, width, height)

class Dial(OneOfElement, Pressable):
    def turn(value: int) -> None: pass
    def down(self) -> None: pass
    def up(self) -> None: pass

class DialSection(PressableSection[Dial]):
    def turn(self, event: DialTurnEvent) -> None:
        if (dial := self._items[event.idx]) is not None:
            dial.turn(event.value)

class StaticImage(Element, Drawable):
    def __init__(self, image: Optional[Image]):
        super().__init__()
        self._image = image

    def set_visible(self) -> None:
        super().set_visible()
        self.draw_image(self._image)

class StaticButton(StaticImage, Button): pass
class StaticTouchscreen(StaticImage, Touchscreen): pass

class BlankElement(Element, Drawable):
    def set_visible(self) -> None:
        super().set_visible()
        self.draw_image(None)

class BlankButton(BlankElement, Button): pass
class BlankTouchscreen(BlankElement, Touchscreen): pass

