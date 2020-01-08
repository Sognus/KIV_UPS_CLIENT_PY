import pygame
import colors

# Resolution of game
HEIGHT = 500
WIDTH = 250

# Player constants
PLAYER_SIZE_WIDTH = 40
PLAYER_SIZE_HEIGHT = 3
PLAYER_SPEED = 5
PLAYER_GAP = 10

# FPS/TPS
FPS = 30


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Set player coords
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE_WIDTH
        self.height = PLAYER_SIZE_HEIGHT

        #
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(colors.BLACK)
        self.image.set_colorkey(colors.BLACK)

        # Draw the car (a rectangle!)
        pygame.draw.rect(self.image, colors.WHITE, [0, 0, self.width, self.height])

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Update coordinates for draw
        self._update_coords()

    def _update_coords(self):
        self.rect.x = self.x - self.width / 2
        self.rect.y = self.y

    def move_right(self, pixels):
        # Check if we can move to right then move
        if self.x + self.width / 2 + pixels <= WIDTH:
            self.x = self.x + pixels
        # Update draw coordinates
        self._update_coords()

    def move_left(self, pixels):
        # Check if we can move to right then move
        if self.x - self.width / 2 - pixels >= 0:
            self.x -= pixels
        # Update draw coordinates
        self._update_coords()


# Start gameloop
def main_loop():
    # Initialize PyGame
    pygame.init()
    # Set programs caption
    pygame.display.set_caption("Pong!")

    # Initialize players
    player1 = Player(WIDTH / 2, PLAYER_GAP)
    player2 = Player(WIDTH / 2, HEIGHT - PLAYER_GAP)

    # Initialize game groups
    all = pygame.sprite.RenderUpdates()
    all.add(player1)
    all.add(player2)

    # Set programs resolution
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

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
        screen.fill(colors.BLACK)

        # draw center line
        pygame.draw.rect(screen, colors.WHITE, [0, HEIGHT / 2, WIDTH, 3])

        # Game render
        all.draw(screen)

        # Update screen
        pygame.display.flip()

        clock.tick(FPS)


def main():
    main_loop()


if __name__ == '__main__':
    main()
