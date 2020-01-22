import pygame
import tkinter
from tkinter import messagebox
from ball import *
from player import *


class Game:

    def __init__(self, player1, player2, ball, context):
        # Player 1 - object
        self.player1 = player1
        # Player 1 - score
        self.score1 = 0
        # Player 2 - object
        self.player2 = player2
        # Player 2 - score
        self.score2 = 0

        # Ball
        self.ball = ball

        # Paused flag
        self.paused = False

        # Server context
        self.context = context

    # Update game state
    def update_state(self, message):
        if message is None:
            return

        # Check message content (LONG)
        player1x = message.get_value("player1x")
        if player1x is None:
            return

        player1y = message.get_value("player1y")
        if player1y is None:
            return

        player2x = message.get_value("player2x")
        if player2x is None:
            return

        player2y = message.get_value("player2y")
        if player2y is None:
            return

        score1 = message.get_value("score1")
        if score1 is None:
            return

        score2 = message.get_value("score2")
        if score2 is None:
            return

        ballx = message.get_value("ballx")
        if ballx is None:
            return

        bally = message.get_value("bally")
        if bally is None:
            return

        ballspeed = message.get_value("ballspeed")
        if ballspeed is None:
            return

        ballrotation = message.get_value("ballrotation")
        if ballrotation is None:
            return

        paused = message.get_value("paused")
        if paused is None:
            return


        # Set game state - players
        try:
            if self.context.playAs == "2":
                # Update player we dont play as
                self.player1.x = float(player1x)
                self.player1.y = float(player1y)
                self.player1.update_coords()

            if self.context.playAs == "1":
                # Update player we dont play as
                self.player2.x = float(player2x)
                self.player2.y = float(player2y)
                self.player2.update_coords()

            # Set game state - score
            self.score1 = int(score1)
            self.score2 = int(score2)

            # Set game state - ball
            self.ball.x = float(ballx)
            self.ball.y = float(bally)
            self.ball.speed = int(ballspeed)
            self.ball.angle = int(ballrotation)
            self.ball.update_coords()

            # Set game state - paused
            self.paused = (paused == "true")
        except Exception as e:
            print(e)


def build_player_update_message(context, game):
    if context is None:
        return ""
    if game is None:
        return ""

    # Get player we play as
    player = None
    if context.playAs == "1":
        player = game.player1
    if context.playAs == "2":
        player = game.player2

    if player is None:
        return ""

    msg = "<id:{};rid:{};type:3000;|x:{};y:{};paused:{};playerID:{};>".format(context.client.messageSent,
                                                                              context.client.messageSent, player.x,
                                                                              player.y, game.paused,
                                                                              context.client.playerID)
    return msg


# Start gameloop
def main_loop(context):
    # Initialize players
    if context.playAs == "1":
        player1 = Player(WIDTH / 2, PLAYER_GAP, control=True)
    else:
        player1 = Player(WIDTH / 2, PLAYER_GAP)

    if context.playAs == "2":
        player2 = Player(WIDTH / 2, HEIGHT - PLAYER_GAP, control=True)
    else:
        player2 = Player(WIDTH / 2, HEIGHT - PLAYER_GAP)

    # Initialize ball
    ball = Ball(WIDTH / 2, HEIGHT / 2, 0)

    # Initialize Game
    context.game = Game(player1, player2, ball, context)

    # Initialize game groups
    all = pygame.sprite.RenderUpdates()
    all.add(player1)
    all.add(player2)
    all.add(ball)

    # Initialize pause text
    font_pause = pygame.font.Font('freesansbold.ttf', 32)
    text_pause = font_pause.render('PAUSED', True, WHITE, BLACK)
    text_pause_rect = text_pause.get_rect()
    text_pause_rect.center = (WIDTH // 2, HEIGHT // 2)

    # Create variable
    context.Running = True

    # Create clock for gameloop
    clock = pygame.time.Clock()

    # main loop
    while context.Running:
        # event handling, gets all event from the event queue
        for event in list(pygame.event.get()):
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                context.menu_game.enable()
                print("game end")
                # Send quit event - ignore response
                msg_abandon = "<id:{};rid:{};type:2500;|playerID:{};>".format(context.client.messageSent,
                                                                      context.client.messageSent,
                                                                      context.client.playerID)
                context.client.socket.send(bytes(msg_abandon, "ascii"))
                context.Running = False

        # Parse all messages
        while context.parser.messages_game and context.Running:
            server_message = context.parser.messages_game.popleft()
            # GameState update message
            if server_message.type == 2400:
                context.game.update_state(server_message)
            if server_message.type == 3100:
                context.Running = False

                # Show alert - main window hidden
                root = tkinter.Tk()
                root.withdraw()

                box_msg = "" if server_message.get_value("msg") is None else server_message.get_value("msg")
                messagebox.showinfo("Game completed", box_msg)

                # kill alert window
                root.destroy()

                context.menu_game.enable()
                print("game completed")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not context.game.paused:
            if context.game.player1.control:
                context.game.player1.move_left(PLAYER_SPEED)
            if context.game.player2.control:
                context.game.player2.move_left(PLAYER_SPEED)

        if keys[pygame.K_RIGHT] and not context.game.paused:
            if context.game.player1.control:
                context.game.player1.move_right(PLAYER_SPEED)
            if context.game.player2.control:
                context.game.player2.move_right(PLAYER_SPEED)

        # Control+Q to end

        # Send current position to server
        msg = build_player_update_message(context, context.game)
        context.client.socket.send(bytes(msg, "ascii"))

        # Clear screen
        context.surface.fill(BLACK)

        # Game logic
        all.update()

        # draw center line
        pygame.draw.rect(context.surface, WHITE, [0, HEIGHT / 2, WIDTH, 1])

        # Game render
        all.draw(context.surface)

        # Draw score
        score_font = pygame.font.Font('freesansbold.ttf', 20)

        score1_string = "{:02d}".format(context.game.score1)
        score1_text = score_font.render(score1_string, True, WHITE, BLACK)
        score1_rect = score1_text.get_rect()
        context.surface.blit(score1_text, (WIDTH - 30, HEIGHT // 2 - 25))

        score2_string = "{:02d}".format(context.game.score2)
        score2_text = score_font.render(score2_string, True, WHITE, BLACK)
        score2_rect = score2_text.get_rect()
        context.surface.blit(score2_text, (WIDTH - 30, HEIGHT // 2 + 5))

        if context.game.paused:
            # Game is paused, draw pause info
            print("PAUSED")
            context.surface.blit(text_pause, text_pause_rect)

        # Update screen
        pygame.display.flip()

        clock.tick(FPS)
