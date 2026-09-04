from typing import Optional
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
from StreamDeck.DeviceManager import StreamDeck, DeviceManager

from .events import ButtonEvent, TouchscreenEventShort, TouchscreenEventLong, TouchscreenEventDrag, DialPushEvent, DialTurnEvent
from .elements import ButtonSection, Touchscreen, DialSection, RootElement

def run(btn_section: Optional[ButtonSection] = None, touchscreen: Optional[Touchscreen] = None, dial_section: Optional[DialSection] = None):
    streamdecks = DeviceManager().enumerate()

    for deck in streamdecks:
        setup_on(deck, btn_section, touchscreen, dial_section)
        return deck

def setup_on(deck: StreamDeck, btn_section: Optional[ButtonSection] = None, touchscreen: Optional[Touchscreen] = None, dial_section: Optional[DialSection] = None):
    if deck.DECK_TYPE != 'Stream Deck +':
        raise NotImplementedError
    
    root = RootElement(deck)

    # callback when dials are pressed or released
    def dial_change_callback(deck, dial, event, value):
        if event == DialEventType.PUSH:
            root.dial_push_update(DialPushEvent(dial, value))
        elif event == DialEventType.TURN:
            root.dial_turn(DialTurnEvent(dial, value))


    # callback when lcd is touched
    def touchscreen_event_callback(deck, evt_type, value):
        x, y = value["x"], value["y"]
        if evt_type == TouchscreenEventType.SHORT:
            event = TouchscreenEventShort(x, y)

        elif evt_type == TouchscreenEventType.LONG:
            event = TouchscreenEventLong(x, y)

        elif evt_type == TouchscreenEventType.DRAG:
            x_out, y_out = value["x_out"], value["y_out"]
            event = TouchscreenEventDrag(x, y, x_out, y_out)

        root.touch_update(event)

    deck.open()
    deck.reset()

    deck.set_key_callback(lambda _, key, key_state: root.btn_update(ButtonEvent(key, key_state)))
    deck.set_dial_callback(dial_change_callback)
    deck.set_touchscreen_callback(touchscreen_event_callback)

    if btn_section is not None: root.set_btns(btn_section)
    if touchscreen is not None: root.set_touchscreen(touchscreen)
    if dial_section is not None: root.set_dials(dial_section)
