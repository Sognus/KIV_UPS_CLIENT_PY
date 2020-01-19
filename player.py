from constants import *
from colors import *
import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y, control=False):
        super().__init__()

        # Flag if player is played
        self.control = control

        # Set player coords
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE_WIDTH
        self.height = PLAYER_SIZE_HEIGHT

        #
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw a player colored by played flag
        color = GREEN if self.control else RED
        pygame.draw.rect(self.image, color, [0, 0, self.width, self.height])

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Update coordinates for draw
        self.update_coords()

    def update_coords(self):
        self.rect.x = self.x - self.width / 2
        self.rect.y = self.y

    def move_right(self, pixels):
        # Check if we can move to right then move
        if self.x + self.width / 2 + pixels <= WIDTH:
            self.x = self.x + pixels
        # Update draw coordinates
        self.update_coords()

    def move_left(self, pixels):
        # Check if we can move to right then move
        if self.x - self.width / 2 - pixels >= 0:
            self.x -= pixels
        # Update draw coordinates
        self.update_coords()
