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

        # TODO:
        #   For every event in parsed message (critical value) process message
        #   Includes things like other players position, ball position and score

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
