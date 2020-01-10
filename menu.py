from constants import *
from colors import *
from client import *
from message import *
import game
import pygame
import pygameMenu

# Global context class
global context


def menu_player_action_test():
    context.menu_game.disable()


def menu_player_action_refresh():
    context.menu_game.disable()

    # Reinitialize menu
    menu_player_init()

    # Add player_menu buttons
    context.menu_game.add_option("TEST", menu_player_action_test)
    context.menu_game.add_option("REFRESH2", menu_player_action_refresh)


def menu_player_init():
    # Connected menu
    context.menu_game = pygameMenu.Menu(context.surface,
                                        bgfun=context.menu_background_draw,
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


def menu_connect_action():
    try:
        data = context.menu_connect.get_input_data()
        context.client = Client(data["ip"], int(data["port"]))
        print("Connection established\n")
        context.parser = MessageParser(context.client)
        context.parser.start()
        context.menu_connect.disable()
    except ConnectionRefusedError:
        print("Could not connect to server - connection refused")
    except ValueError:
        print("Could not connect to server - bad input data")
    except Exception as e:
        print(f"Could not connect to server - {e}")


def menu_start(client_context):
    # GLOBAL CLIENT CONTEXT
    global context
    context = client_context

    global test
    test = 0

    # INIT PYGAME
    pygame.init()

    client_context.surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong!")
    client_context.clock = pygame.time.Clock()

    # CONNECT MENU
    context.menu_connect = pygameMenu.Menu(context.surface,
                                           bgfun=client_context.menu_background_draw,
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
    context.menu_connect.add_text_input("Name: ", default="", maxchar=20, textinput_id="name")
    context.menu_connect.add_text_input("IP: ", default="127.0.0.1", maxchar=15, textinput_id="ip")
    context.menu_connect.add_text_input("Port: ", default="8080", maxchar=5, textinput_id="port")
    context.menu_connect.add_option("CONNECT", menu_connect_action)

    # Connected menu
    menu_player_init()

    # Add player_menu buttons
    client_context.menu_game.add_option("TEST", menu_player_action_test)
    client_context.menu_game.add_option("REFRESH", menu_player_action_refresh)

    # -------------------------------------------------------------------------
    # Start menu
    # -------------------------------------------------------------------------

    while True:
        # Clear draw area
        context.surface.fill(BLACK)

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit(0)

        if context.menu_connect.is_enabled():
            # Connection menu
            context.menu_connect.mainloop(events)
        else:
            if context.menu_game.is_enabled():
                # Player menu - Starts after Connect menu is disabled
                context.menu_game.mainloop(events)
            else:
                # Main game loop
                game.main_loop(context)

        # Flip surface
        pygame.display.flip()
