import asyncio
from PIL import Image, ImageDraw

from streamdeck_gui.setup import init_first
from streamdeck_gui.image import ButtonImage, TouchscreenImage
from streamdeck_gui.elements import StaticButton, ButtonSection, StaticTouchscreen, BlankButton, BlankTouchscreen
from streamdeck_gui.menu import Menu, MenuController

class CallbackButton(StaticButton):
    def __init__(self, image, callback):
        super().__init__(image)
        self._callback = callback

    def up(self): self._callback(self)

def draw_text_centered(image: Image.Image, text: str, font_size: int = 30) -> None:
    draw = ImageDraw.Draw(image)
    w, h = image.size
    draw.text((w / 2, h / 2), text, font_size=font_size, anchor="mm")

def button_image_with_text(text: str, font_size: int = 30) -> ButtonImage:
    image = Image.new("RGB", ButtonImage.size)
    draw_text_centered(image, text, font_size)
    return ButtonImage(image)

touchscreen = StaticTouchscreen(TouchscreenImage.from_file("btn.webp"))

async def main():
    deck, root = init_first()
    menu_controller = MenuController(root)
    actions_menu = Menu(
        ButtonSection(
            CallbackButton(button_image_with_text("Btn 1"), lambda _: print("Button 1")),
            CallbackButton(button_image_with_text("Btn 2"), lambda _: print("Button 2")),
            BlankButton(), BlankButton(),
            CallbackButton(button_image_with_text("Home"), lambda _: menu_controller.home()),
            BlankButton(), BlankButton(),
            CallbackButton(button_image_with_text("Back"), lambda _: menu_controller.back()),
        ),
        touchscreen
    )
    home_menu = Menu(
        ButtonSection(
            CallbackButton(button_image_with_text("Actions"), lambda _: menu_controller.show(actions_menu)),
            *(BlankButton() for _ in range(7))
        )
    )
    menu_controller.show(home_menu)
    await deck.wait()

if __name__ == "__main__": asyncio.run(main())
