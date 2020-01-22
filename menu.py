import sys
import tkinter
from tkinter import messagebox
from constants import *
from colors import *
from client import *
from message import *
from datetime import datetime
import game
import pygame
import pygameMenu
import re

# Global context class
global context


class KeepAliveThread(threading.Thread):

    def __init__(self, client, context):
        super().__init__()
        self.client = client
        self.context = context
        self.running = True

    def run(self):
        try:
            while self.running:
                msg = "<id:0;rid:0;type:1100;|status:ok;>"
                self.client.socket.send(bytes(msg, "ascii"))
                time.sleep(0.5)
                # Retreive keepalive
                while context.parser.messages_keepalive:
                    message = context.parser.messages_keepalive.popleft()
                    self.client.keepAlive = time.time()

        except socket.error as e:
            self.client.keepAlive = 0
            print("KeepAliveErr: " + str(self.client.is_connected()))
            # Put player into menu
            self.context.menu_connect.enable()
            self.context.menu_game.disable()
            # Stop game
            self.context.Running = False


def show_alert_info(title, message):
    # Show alert - main window hidden
    root = tkinter.Tk()
    root.withdraw()

    messagebox.showinfo(title, message)

    # kill alert window
    root.destroy()


# Empty action to satisfy buttons
def menu_nothing():
    pass


def menu_player_action_game_join(gameID):
    # gameID = ID if game to join
    print("Requesting game join")

    request_id = context.client.messageSent
    request_msg = "<id:{};rid:{};type:2100;|playerID:{};gameID:{};>".format(request_id, request_id,
                                                                            context.client.playerID, gameID)
    try:
        context.client.socket.send(bytes(request_msg, "ascii"))
    except:
        pass
    context.client.messageSent = request_id + 1

    # Wait for response maximum of 2 sec
    message = None
    start = datetime.now()
    wait = True
    while wait:
        for msg in list(context.parser.messages):
            if int(msg.id) == int(request_id):
                message = msg
                wait = False
                break
        check = datetime.now()
        delta = check - start
        if delta.total_seconds() > 2:
            wait = False

    if message is None:
        print("Cannot join game - wait for response timed out")
        show_alert_info("Cannot join game" , "Wait for server response timed out!")
    else:
        status = message.get_value("status")
        if status is None:
            print("Cannot join game - bad server response")
            show_alert_info("Cannot join game", "Bad server response")
        else:
            # Game join?
            if status == "ok":
                # Indicate who as player playing as
                playAs = message.get_value("player")
                if playAs is None:
                    print("Cannot create game - bad server response")
                    show_alert_info("Cannot join game", "Bad server response!")
                else:
                    context.playAs = playAs
                    # Enable game
                    context.menu_game.disable()
            else:
                status_msg = "unknown error" if message.get_value("msg") is None else message.get_value("msg")
                print("Game was not joined: " + status_msg)
                show_alert_info("Cannot join game", status_msg)


# TODO: Implement
def menu_player_action_game_create():
    print("Requesting game create")

    # Send request to server to join game
    request_id = context.client.messageSent
    request_msg = "<id:{};rid:{};type:2000;|playerID:{};>".format(request_id, request_id, context.client.playerID)
    try:
        context.client.socket.send(bytes(request_msg, "ascii"))
    except:
        pass
    context.client.messageSent = request_id + 1

    # Wait for response maximum of 2 sec
    message = None
    start = datetime.now()
    wait = True
    while wait:
        for msg in list(context.parser.messages):
            if int(msg.id) == int(request_id):
                message = msg
                wait = False
                break
        check = datetime.now()
        delta = check - start
        if delta.total_seconds() > 2:
            wait = False

    if message is None:
        print("Cannot create game - wait for response timed out")
        show_alert_info("Cannot create game" , "Wait for server response timed out!")
    else:
        status = message.get_value("status")
        if status is None:
            print("Cannot create game - bad server response")
            show_alert_info("Cannot create game", "Bad server response")
        else:
            # Game created
            if status == "ok":
                # Indicate who as player playing as
                context.playAs = "1"
                # Enable game
                context.menu_game.disable()
            else:
                status_msg = "unknown error" if message.get_value("msg") is None else message.get_value("msg")
                print("Game was not created: " + status_msg)
                show_alert_info("Cannot create game", status_msg)


def menu_player_action_disconnect():
    request_disconnect(context)
    context.menu_game.disable()
    context.menu_connect.enable()


def menu_player_action_refresh():
    # Disable game menu if its enabled
    try:
        context.menu_game.disable()
    except:
        pass

    # Reinitialize menu
    menu_player_init()

    # Add button to join game
    context.menu_game.add_option("CREATE GAME", menu_player_action_game_create)

    # Ask server for game IDS
    request_id = context.client.messageSent
    request_msg = "<id:{};rid:{};type:2300;|playerID:{};>".format(request_id, request_id, context.client.playerID)
    try:
        context.client.socket.send(bytes(request_msg, "ascii"))
    except:
        pass
    context.client.messageSent = request_id + 1

    # Wait for response maximum of 2 sec
    message = None
    start = datetime.now()
    wait = True
    while wait:
        for msg in list(context.parser.messages):
            if int(msg.id) == int(request_id):
                message = msg
                wait = False
        check = datetime.now()
        delta = check - start
        if delta.total_seconds() > 2:
            wait = False

    # ID List
    id_list = list()

    id_base = r"gameID(\d+)"
    id_pattern = re.compile(id_base)

    # We have message - we add it to ID List
    if message is not None:
        for key in message.content:
            if re.match(id_pattern, str(key)):
                print(key)
                id_list.append(message.content[key])

    # If ID list is empty
    if len(id_list) < 1:
        context.menu_game.add_option("NO GAMES AVAILABLE", menu_nothing)
    else:
        # Build selector
        for id in id_list:
            name = "GAME #{}".format(id)
            context.menu_game.add_option(name, menu_player_action_game_join, id)

    # Add player_menu buttons
    context.menu_game.add_option("REFRESH", menu_player_action_refresh)

    # Disconnect button
    context.menu_game.add_option("DISCONNECT", menu_player_action_disconnect)


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

def menu_reconnect_action():
    try:
        data = context.menu_connect.get_input_data()

        if len(data["name"]) < 1:
            show_alert_info("Cannot reconnect", "Name cannot be empty")
            print("Could not connect to server - name cannot be empty!")
            return

        context.client = Client(data["ip"], int(data["port"]))
        print("Connection reestablished\n")
        context.parser = MessageParser(context.client)
        context.parser.start()

        # Send register request
        request_id = context.client.messageSent
        register_msg = "<id:{};rid:{};type:2200;|username:{};>".format(request_id, request_id, data["name"])
        try:
            context.client.socket.send(bytes(register_msg, "ascii"))
        except:
            pass

        # Wait for response maximum of 2 sec
        message = None
        start = datetime.now()
        wait = True
        while wait:
            for msg in list(context.parser.messages):
                if int(msg.id) == int(request_id):
                    message = msg
                    wait = False
            check = datetime.now()
            delta = check - start
            if delta.total_seconds() > 60:
                wait = False

        if message is not None:
            if message.get_value("status") == "ok":
                gameID = message.get_value("gameID")
                playerID = message.get_value("playerID")
                playAs = message.get_value("playas")

                if playerID is None:
                    raise Exception("Malformed response from server - missing playerID")

                # Reset playerID
                context.client.playerID = int(playerID)

                # Start keepalive thread
                context.keepalive_thread = KeepAliveThread(context.client, context)
                context.keepalive_thread.daemon = True
                context.keepalive_thread.start()

                # We have info about playas and gameID
                if gameID is not None and playAs is not None:
                    context.playAs = playAs
                    # Enable game
                    context.menu_connect.disable()
                    context.menu_game.disable()

                else:
                    # Player is not connected to game - put him in game menu
                    context.menu_connect.disable()
                    context.menu_game.enable()

            else:
                raise Exception("Could not connect to server - {}".format(message.get_value("msg")))
        else:
            raise Exception("no valid response from server")

    except ConnectionRefusedError:
        print("Could not reconnect to server - connection refused")
        request_disconnect(context)
        show_alert_info("Cannot reconnect", "Connection refused")
    except ValueError:
        print("Could not reconnect to server - bad input data")
        request_disconnect(context)
        show_alert_info("Cannot reconnect", "Wrong response data format")
    except Exception as e:
        print(f"Could not reconnect to server - {e}")
        request_disconnect(context)
        show_alert_info("Cannot reconnect", str(e))



def menu_connect_action():
    try:
        data = context.menu_connect.get_input_data()

        if len(data["name"]) < 1:
            show_alert_info("Cannot connect to server", "Name cannot be empty")
            print("Could not connect to server - name cannot be empty!")
            return

        context.client = Client(data["ip"], int(data["port"]))
        print("Connection established\n")
        context.parser = MessageParser(context.client)
        context.parser.start()

        # Send register request
        request_id = context.client.messageSent
        register_msg = "<id:{};rid:{};type:1000;|name:{};>".format(request_id, request_id, data["name"])
        try:
            context.client.socket.send(bytes(register_msg, "ascii"))
        except:
            pass

        # Wait for response maximum of 2 sec
        message = None
        start = datetime.now()
        wait = True
        while wait:
            for msg in list(context.parser.messages):
                if int(msg.id) == int(request_id):
                    message = msg
                    wait = False
            check = datetime.now()
            delta = check - start
            if delta.total_seconds() > 2:
                wait = False

        if message is not None:
            if message.get_value("status") == "ok":
                playerID = int(message.get_value("playerID"))
                context.client.playerID = playerID
                print("Connected to server as player ID: {}".format(playerID))

                context.username = data["name"]

                # Start keepalive thread
                context.keepalive_thread = KeepAliveThread(context.client, context)
                context.keepalive_thread.daemon = True
                context.keepalive_thread.start()

                context.menu_connect.disable()
                context.menu_game.enable()
            else:
                raise Exception("Could not connect to server - {}".format(message.get_value("msg")))
        else:
            raise Exception("no valid response from server")

    except ConnectionRefusedError:
        print("Could not connect to server - connection refused")
        request_disconnect(context)
        show_alert_info("Cannot connect to server", "Connection refused")
    except ValueError:
        print("Could not connect to server - bad input data")
        request_disconnect(context)
        show_alert_info("Cannot connect to server", "Wrong response format")
    except Exception as e:
        print(f"Could not connect to server - {e}")
        request_disconnect(context)
        show_alert_info("Cannot connect to server", str(e))


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
    connect_username = "" if context.username is None else context.username

    context.menu_connect.add_text_input("Name: ", default=connect_username, maxchar=20, textinput_id="name")
    context.menu_connect.add_text_input("IP: ", default="192.168.0.200", maxchar=15, textinput_id="ip")
    context.menu_connect.add_text_input("Port: ", default="8080", maxchar=5, textinput_id="port")
    context.menu_connect.add_option("CONNECT", menu_connect_action)
    context.menu_connect.add_option("RECONNECT", menu_reconnect_action)

    # Connected menu
    menu_player_init()

    # -------------------------------------------------------------------------
    # Start menu
    # -------------------------------------------------------------------------

    while True:
        # Clear draw area
        context.surface.fill(BLACK)

        # Application events
        events = list(pygame.event.get())

        if context.menu_connect.is_enabled():
            # Connection menu
            context.menu_connect.mainloop(events)
        else:
            if context.menu_game.is_enabled():
                # Player menu - Starts after Connect menu is disabled
                menu_player_action_refresh()
                context.menu_game.mainloop()
            else:
                # Main game loop
                game.main_loop(context)


        # Flip surface
        pygame.display.flip()
