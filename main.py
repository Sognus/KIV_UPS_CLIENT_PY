from colors import BLACK
from menu import *


# Class that holds information - easier to move all data
class Context:

    def __init__(self):
        # Games draw area
        self.surface = None
        # Games TCP client
        self.client = None
        # Connect menu
        self.menu_connect = None
        # Game menu
        self.menu_game = None
        # Games clock
        self.clock = None
        # Message parser
        self.parser = None

    def menu_background_draw(self):
        if self.surface is not None:
            self.surface.fill(BLACK)


def main():
    client_context = Context()
    menu_start(client_context)


if __name__ == '__main__':
    main()
