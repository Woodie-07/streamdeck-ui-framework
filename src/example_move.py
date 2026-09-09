import asyncio
import itertools

from streamdeck_gui.setup import setup_first
from streamdeck_gui.image import ButtonImage, TouchscreenImage
from streamdeck_gui.elements import StaticButton, ButtonSection, StaticTouchscreen, BlankButton

async def deck_loop(button_section: ButtonSection):
    for i in itertools.cycle(range(8)):
        await asyncio.sleep(0.1)
        button_section.set((i + 1) % 8, button_section.set(i, BlankButton()))

async def main():
    button_section = ButtonSection(StaticButton(ButtonImage.from_file("btn.webp")))
    asyncio.create_task(deck_loop(button_section))
    if deck := setup_first(button_section, StaticTouchscreen(TouchscreenImage.from_file("btn.webp"))):
        await deck.wait()

if __name__ == "__main__": asyncio.run(main())
