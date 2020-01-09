from constants import *
from colors import *
from player import *
import pygame


# Start gameloop
def main_loop(context):

    # Initialize players
    player1 = Player(WIDTH / 2, PLAYER_GAP)
    player2 = Player(WIDTH / 2, HEIGHT - PLAYER_GAP)

    # Initialize game groups
    all = pygame.sprite.RenderUpdates()
    all.add(player1)
    all.add(player2)

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

        #
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player1.move_left(PLAYER_SPEED)
        if keys[pygame.K_RIGHT]:
            player1.move_right(PLAYER_SPEED)
        if keys[pygame.K_a]:
            player2.move_left(PLAYER_SPEED)
        if keys[pygame.K_d]:
            player2.move_right(PLAYER_SPEED)

        # Game logic
        all.update()

        # Clear clear
        context.surface.fill(BLACK)

        # draw center line
        pygame.draw.rect(context.surface, WHITE, [0, HEIGHT / 2, WIDTH, 3])

        # Game render
        all.draw(context.surface)

        # Update screen
        pygame.display.flip()

        clock.tick(FPS)
