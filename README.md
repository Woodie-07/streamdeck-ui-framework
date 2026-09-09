This library aims to make it easier to build complex UI layouts with multiple menus and interactivity for the Stream Deck, built on top of the python-elgato-streamdeck library. It's currently only compatible with the Stream Deck + but could probably be pretty easily modified to work with other models. Expect things to change as this is early in development and has some issues.

Currently, there are three examples:
- `example_move.py` - runs on the first Stream Deck found, displays a static image on the touchscreen and the same image on one of the 8 buttons, moving to the next button along every ~0.1 seconds in a loop.
- `example_ssh.py` - runs on all Stream Decks found, logs all input to the 4 dials, displays a static image on the touchscreen and logs touchscreen input, and displays 8 SSH hosts on the buttons which have their current status indicated by their background colour and which can be opened by pressing the button.
- `example_menu.py` - has a home page with a blank touchscreen with one button that takes you to a different page with two buttons which print to console, along with home and back buttons to take you back to the home page.

All examples are designed to work with my fork of the python-elgato-streamdeck library, but could be made to work with the original pretty easily.

Images can be reused. Elements cannot be in multiple places at once. Sections can be in multiple menus as long as the menus are never active simultaneously (multiple devices).

Since the elements themselves are responsible for drawing, you should use BlankButton/BlankTouchscreen when you want to clear anything that was previously there. If using the menu system, the Menu will initialise unprovided sections to Blanks where required. Though, BlankButtons should still be used for unused button spaces in any provided ButtonSection.
