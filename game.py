from constants import *
from colors import *
from player import *
from ball import *
import pygame


class Game:

    def __init__(self, player1, player2, ball):
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

        # Game - paused flag
        self.paused = True

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

        print("message checked updating game state")

        # Set game state - players
        try:
            self.player1.x = int(player1x)
            self.player1.y = int(player1y)

            self.player2.x = int(player2x)
            self.player2.y = int(player2y)

            # Set game state - score
            self.score1 = int(score1)
            self.score2 = int(score2)

            # Set game state - ball
            self.ball.x = int(ballx)
            self.ball.y = int(bally)
            self.ball.speed = int(ballspeed)
            self.ball.angle = int(ballrotation)

            # Set game state - paused
            self.paused = False
        except:
            pass



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
    game = Game(player1, player2, ball)

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
    running = True

    # Create clock for gameloop
    clock = pygame.time.Clock()

    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                context.menu_game.enable()
                print("game end")
                running = False

        # Parse all messages
        if context.parser.messages_game:
            server_message = context.parser.messages_game.popleft()
            # GameState update message
            if server_message.type == 2400:
                game.update_state(server_message)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if game.player1.control:
                game.player1.move_left(PLAYER_SPEED)
            if game.player2.control:
                game.player2.move_left(PLAYER_SPEED)

        if keys[pygame.K_RIGHT]:
            if game.player1.control:
                game.player1.move_right(PLAYER_SPEED)
            if game.player2.control:
                game.player2.move_right(PLAYER_SPEED)

        if keys[pygame.K_u]:
            game.paused = not game.paused

        # TODO:
        #   Send message with current position (only played player position)

        # Clear screen
        context.surface.fill(BLACK)

        if game.paused:
            # Game is paused, draw pause info
            context.surface.blit(text_pause, text_pause_rect)
        else:
            # Game logic
            all.update()

            # Clear clear
            context.surface.fill(BLACK)

            # draw center line
            pygame.draw.rect(context.surface, WHITE, [0, HEIGHT / 2, WIDTH, 1])

            # Game render
            all.draw(context.surface)

            # Draw score
            score_font = pygame.font.Font('freesansbold.ttf', 20)

            score1_string = "{:02d}".format(game.score1)
            score1_text = score_font.render(score1_string, True, WHITE, BLACK)
            score1_rect = score1_text.get_rect()
            context.surface.blit(score1_text, (WIDTH - 30, HEIGHT // 2 - 25))

            score2_string = "{:02d}".format(game.score2)
            score2_text = score_font.render(score2_string, True, WHITE, BLACK)
            score2_rect = score2_text.get_rect()
            context.surface.blit(score2_text, (WIDTH - 30, HEIGHT // 2 + 5))

        # Update screen
        pygame.display.flip()

        clock.tick(FPS)
