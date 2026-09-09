from dataclasses import dataclass, field
from typing import Optional, List

from .elements import RootElement, ButtonSection, Touchscreen, DialSection, BlankTouchscreen, BlankButton

@dataclass
class Menu:
    buttons: Optional[ButtonSection] = field(default_factory=lambda: ButtonSection(*(BlankButton() for _ in range(8))))
    touchscreen: Optional[Touchscreen] = field(default_factory=BlankTouchscreen)
    dials: Optional[DialSection] = None

    def on_enter(self) -> None: pass
    def on_exit(self) -> None: pass

class MenuController:
    def __init__(self, root: RootElement):
        self._root = root
        self._stack: List[Menu] = []

    def _render(self, menu: Menu) -> None:
        self._root.set_sections(menu.buttons, menu.touchscreen, menu.dials)

    def show(self, menu: Menu) -> None:
        if self._stack: self._stack[-1].on_exit()
        self._stack.append(menu)
        menu.on_enter()
        self._render(menu)

    def _goto(self, idx: int) -> bool:
        try:
            new = self._stack[idx]
        except IndexError:
            return False
        if new == self._stack[-1]: return False

        prev = self._stack.pop()
        prev.on_exit()
        new.on_enter()
        self._render(new)
        return True

    def back(self) -> bool:
        return self._goto(-2)

    def home(self) -> bool:
        return self._goto(0)
