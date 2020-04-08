import pygame
from pygame.sprite import Sprite
import os
import math
from pygame.math import Vector2


class Car(Sprite):
    def __init__(self, image_path, pos, angle):
        super(Car, self).__init__()
        original_image = pygame.image.load(os.path.join(image_path)).convert_alpha()
        self.original_image = pygame.transform.rotozoom(original_image, 0, 0.08)
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=pos)

        self.speed = 5
        self.angle_speed = 0
        self.position = Vector2(pos)
        self.angle = angle
        self.direction = Vector2(1, 0)  # A unit vector pointing rightward.
        self.direction.rotate_ip(angle)

    def update(self, dt):
        if self.angle_speed != 0:
            # Rotate the direction vector and then the image.
            self.direction.rotate_ip(self.angle_speed)
            self.angle += self.angle_speed
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        # Update the position vector and the rect.
        self.position += self.direction * self.speed
        self.rect.center = self.position
