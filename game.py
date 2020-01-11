from constants import *
from colors import *
from player import *
import pygame


class Game:

    def __init__(self, player1, player2):
        # Player 1 - object
        self.player1 = player1
        # Player 1 - score
        self.score1 = 0
        # Player 2 - object
        self.player2 = player2
        # Player 2 - score
        self.score2 = 0

        # Game - paused flag
        self.paused = True


# Start gameloop
def main_loop(context):
    # Initialize players
    player1 = Player(WIDTH / 2, PLAYER_GAP)
    player2 = Player(WIDTH / 2, HEIGHT - PLAYER_GAP)

    # Initialize Game
    game = Game(player1, player2)

    # Initialize game groups
    all = pygame.sprite.RenderUpdates()
    all.add(player1)
    all.add(player2)

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
                running = False

        # TODO:
        #   For every event in parsed message (critical value) process message
        #   Includes things like other players position, ball position and score

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.player1.move_left(PLAYER_SPEED)
        if keys[pygame.K_RIGHT]:
            game.player1.move_right(PLAYER_SPEED)
        if keys[pygame.K_a]:
            game.player2.move_left(PLAYER_SPEED)
        if keys[pygame.K_d]:
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

        # Update screen
        pygame.display.flip()

        clock.tick(FPS)
