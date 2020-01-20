from colors import *
from constants import *
import pygame
import math


class Ball(pygame.sprite.Sprite):

    def __init__(self, x, y, angle):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = 45
        self.speed = 5
        self.maxspeed = 30

        # Setup size - radius
        self.size = BALL_SIZE

        # Setup surface
        self.image = pygame.Surface([self.size * 2, self.size * 2])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw circle
        pygame.draw.circle(self.image, PURPLE, [self.size,self.size], self.size, 0)

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Update draw coordianates
        self.update_coords()

    # Update draw coordiantes
    def update_coords(self):
        # Set coords of object
        self.rect.x = self.x - self.size
        self.rect.y = self.y - self.size

    def update(self):
        self.update_coords()
