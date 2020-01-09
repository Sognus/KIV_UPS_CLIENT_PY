from constants import *
from colors import *
from client import *
import game
import pygame
import pygameMenu

# Global variables
global player_menu
global connect_menu

global client
global surface


def main_background():
    """
    Function used by menus, draw on background while menu is active.
    :return: None
    """
    global surface
    surface.fill(BLACK)


def menu_player_action_test():
    player_menu.disable()
    game.main_loop(surface)


def menu_connect_action():
    try:
        global client

        data = connect_menu.get_input_data()
        client = Client(data["ip"], int(data["port"]))

        print("Connection established")

        connect_menu.disable()
    except ConnectionRefusedError:
        print("Could not connect to server - connection refused")
    except ValueError:
        print("Could not connect to server - bad input data")
    except Exception as e:
        print(f"Could not connect to server - {e}")


def main_menu():
    # GLOBALS
    global clock
    global main_menu
    global surface

    # INIT PYGAME
    pygame.init()

    # CREATE PYGAME SCREEN AND OBJECTS
    global surface
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong!")
    clock = pygame.time.Clock()

    # CONNECT MENU
    global connect_menu
    connect_menu = pygameMenu.Menu(surface,
                                   bgfun=main_background,
                                   color_selected=WHITE,
                                   font=pygameMenu.font.FONT_BEBAS,
                                   font_color=WHITE,
                                   font_size=40,
                                   font_size_title=30,
                                   menu_alpha=100,
                                   menu_color=(20, 67, 109),
                                   menu_height=HEIGHT,
                                   menu_width=WIDTH,
                                   onclose=pygameMenu.events.DISABLE_CLOSE,
                                   option_shadow=False,
                                   title='MENU',
                                   window_height=HEIGHT,
                                   window_width=WIDTH,
                                   back_box=False,
                                   menu_color_title=(20, 32, 52),
                                   )

    # Add Menu input
    connect_menu.add_text_input("IP: ", default="127.0.0.1", maxchar=15, textinput_id="ip")
    connect_menu.add_text_input("Port: ", default="8080", maxchar=5, textinput_id="port")
    connect_menu.add_option("CONNECT", menu_connect_action)

    # configure menu
    connect_menu.set_fps(FPS)

    # Connected menu
    global player_menu
    player_menu = pygameMenu.Menu(surface,
                                  bgfun=main_background,
                                  color_selected=WHITE,
                                  font=pygameMenu.font.FONT_BEBAS,
                                  font_color=WHITE,
                                  font_size=40,
                                  font_size_title=30,
                                  menu_alpha=100,
                                  menu_color=(20, 67, 109),
                                  menu_height=HEIGHT,
                                  menu_width=WIDTH,
                                  onclose=pygameMenu.events.DISABLE_CLOSE,
                                  option_shadow=False,
                                  title='GAME',
                                  window_height=HEIGHT,
                                  window_width=WIDTH,
                                  back_box=False,
                                  menu_color_title=(20, 32, 52),
                                  )

    # Add player_menu buttons
    player_menu.add_option("TEST", menu_player_action_test)

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    while True:

        # Tick
        clock.tick(FPS)

        # Paint background
        main_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        connect_menu.mainloop(events)
        # Player menu - After connection
        player_menu.mainloop(events)

        # Flip surface
        pygame.display.flip()
