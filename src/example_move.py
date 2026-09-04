import asyncio
import itertools

from streamdeck_gui.setup import run
from streamdeck_gui.elements import StaticButton, ButtonImage, ButtonSection, StaticTouchscreen, TouchscreenImage

async def deck_loop(button_section: ButtonSection):
    for i in itertools.cycle(range(8)):
        await asyncio.sleep(0.1)
        button_section.set((i + 1) % 8, button_section.remove(i))

async def main():
    button_section = ButtonSection()
    button_section.set(0, StaticButton(ButtonImage.from_file("btn.webp")))
    asyncio.create_task(deck_loop(button_section))
    await run(button_section, StaticTouchscreen(TouchscreenImage.from_file("btn.webp"))).wait()

if __name__ == "__main__": asyncio.run(main())
