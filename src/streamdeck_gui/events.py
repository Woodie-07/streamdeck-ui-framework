from dataclasses import dataclass
from abc import ABC

class PressEvent(ABC):
    idx: int
    pressed: bool

@dataclass
class ButtonEvent(PressEvent):
    idx: int
    pressed: bool

@dataclass
class TouchscreenEvent:
    x: int
    y: int

class TouchscreenEventShort(TouchscreenEvent): pass
class TouchscreenEventLong(TouchscreenEvent): pass

@dataclass
class TouchscreenEventDrag(TouchscreenEvent):
    end_x: int
    end_y: int

@dataclass
class DialEvent:
    idx: int

@dataclass
class DialTurnEvent(DialEvent):
    value: int

@dataclass
class DialPushEvent(DialEvent, PressEvent):
    pressed: bool
