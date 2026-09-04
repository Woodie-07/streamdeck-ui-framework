import asyncio
import subprocess
from StreamDeck.DeviceManager import DeviceManager
from PIL import Image
from typing import Optional

from streamdeck_gui.setup import setup
from streamdeck_gui.elements import ButtonSection, VisibilityAwareButton, StaticTouchscreen, TouchscreenImage, DialSection, Dial
from streamdeck_gui.events import TouchscreenEvent
from streamdeck_gui.image import PillowImage

def ssh_to(host: str):
    script = f'''
tell application "Terminal"
    activate
    do script "ssh {host}"
end tell
    '''
    subprocess.run(["osascript", "-e", script])

async def is_ssh_up(host: str):
    proc = await asyncio.create_subprocess_exec(
        "/opt/homebrew/bin/ssh",
        "-o", "BatchMode=yes",
        "-o", "PubkeyAuthentication=no",
        "-o", "PasswordAuthentication=no",
        "-o", "KbdInteractiveAuthentication=no", 
        "-o", "ChallengeResponseAuthentication=no",
        "-o", "ConnectTimeout=5",
        host, 
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return b"Permission denied" in stderr

class SSHHost:
    def __init__(self, name: str):
        self._name = name

    async def is_up(self) -> bool:
        return await is_ssh_up(self._name)

    def open(self) -> None:
        ssh_to(self._name)

class ServiceButton(VisibilityAwareButton):
    WHITE_IMG = PillowImage(Image.new("RGB", (120, 120), "WHITE"))

    @staticmethod
    def _build_img_with_bg(icon: Image, bg_colour: str) -> PillowImage:
        img = Image.new("RGBA", icon.size, bg_colour)
        img.paste(icon, (0, 0), icon)
        return PillowImage(img)

    def __init__(self, service: SSHHost, icon: Image.Image):
        super().__init__()
        self._service = service
        icon = icon.resize((120, 120)).convert("RGBA")
        self._ok_image = self._build_img_with_bg(icon, "BLACK")
        self._unk_image = self._build_img_with_bg(icon, "PURPLE")
        self._bad_image = self._build_img_with_bg(icon, "RED")
        self._state: Optional[bool] = None
        self._visible = False
        self._down = False
        asyncio.create_task(self._probe_loop())

    async def _probe_loop(self):
        while True:
            old_state = self._state
            self._state = await self._service.is_up()
            if not self._down and old_state != self._state and self._visible:
                self._draw_image(self._ok_image if self._state else self._bad_image) 
            await asyncio.sleep(10)

    def get_image(self) -> PillowImage:
        match self._state:
            case True: return self._ok_image
            case False: return self._bad_image
            case None: return self._unk_image

    def set_visible(self) -> None:
        super().set_visible()
        self._draw_image(self.get_image()) 

    def down(self) -> None:
        self._down = True
        self._draw_image(self.WHITE_IMG)
        asyncio.get_running_loop().run_in_executor(None, self._service.open)

    def up(self) -> None:
        self._draw_image(self.get_image())

class LogTouchscreen(StaticTouchscreen):
    IMAGE = TouchscreenImage.from_file("btn.webp")
    def update(self, event: TouchscreenEvent) -> None:
        print(event)

class LogDial(Dial):
    def up(self) -> None: print(f"{self._idx} dial up")

    def down(self) -> None: print(f"{self._idx} dial down")

    def turn(self, value: int) -> None: print(f"{self._idx} dial turn {value}")

async def main():
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    decks = set()
    for index, deck in enumerate(streamdecks):
        pi_img = Image.open("pi.png").resize((120, 120))
        server_img = Image.open("server.png").resize((120, 120))
        setup(deck, ButtonSection([
            ServiceButton(SSHHost("pi"), pi_img),
            *(ServiceButton(SSHHost(name), server_img) for name in ("server1", "server2", "server3", "server4", "server5", "server6", "server7"))
        ]), LogTouchscreen(), DialSection([LogDial() for _ in range(4)]))
        decks.add(deck)

    for deck in decks: await deck.wait()

if __name__ == "__main__":
    asyncio.run(main())
