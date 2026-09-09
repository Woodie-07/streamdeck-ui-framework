from typing import Optional
from StreamDeck.DeviceManager import StreamDeck, DeviceManager

from .elements import ButtonSection, Touchscreen, DialSection, RootElement
from .menu import MenuController, Menu

def setup_first(btn_section: Optional[ButtonSection] = None, touchscreen: Optional[Touchscreen] = None, dial_section: Optional[DialSection] = None) -> Optional[StreamDeck]:
    deck, root = init_first()
    if deck is None: return None
    root.set_sections(btn_section, touchscreen, dial_section)
    return deck

def init_first():
    streamdecks = DeviceManager().enumerate()

    for deck in streamdecks:
        return deck, init_on(deck)
    return None, None

def init_on(deck: StreamDeck) -> RootElement:
    if deck.DECK_TYPE != 'Stream Deck +':
        raise NotImplementedError

    deck.open()
    deck.reset()
    
    root = RootElement(deck)
    return root
