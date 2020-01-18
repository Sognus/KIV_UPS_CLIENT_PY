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
        self.size = 10

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
        """"
        # TODO: Move logic to server
        radians = self.angle * (math.pi / 180)
        velocity_x = math.cos(radians)
        velicity_y = math.sin(radians)
        self.x += velocity_x * self.speed
        self.y += velicity_y * self.speed

        # Bounce
        if self.x >= WIDTH or self.x <= 0:
            self.angle = 180 - self.angle
            if self.speed <= self.maxspeed:
                self.speed += 3
        if self.y >= HEIGHT or self.y <= 0:
            self.angle = 360 - self.angle
            if self.speed <= self.maxspeed:
                self.speed += 3
        """
