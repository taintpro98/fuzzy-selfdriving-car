import pygame
from pygame.sprite import Sprite
import os
import math
from pygame.math import Vector2


class Car(Sprite):
    def __init__(self, image_path):
        super(Car, self).__init__()
        original_image = pygame.image.load(os.path.join(image_path)).convert_alpha()
        self.original_image = pygame.transform.rotozoom(original_image, 0, 0.08)
        self.width = self.original_image.get_rect().width
        self.height = self.original_image.get_rect().height
        self.speed = 5
        self.angle_speed = 0
        self.display = False
        
    def init_position(self, pos, angle):
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.angle = angle
        self.direction = Vector2(1, 0)  # A unit vector pointing rightward.
        self.direction.rotate_ip(angle)
        self.display = True

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

    def get_variables(self):
        variables = {}
        return variables

    def get_polygon(self):
        c = self.rect.center

        topleft_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        topleft_vec = topleft_vec.rotate(self.angle)
        topleft = (c[0] + topleft_vec.x, c[1] + topleft_vec.y)

        topright_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        topright_vec = topright_vec.rotate(self.angle)
        topright = (c[0] + topright_vec.x, c[1] + topright_vec.y)

        bottomleft_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        bottomleft_vec = bottomleft_vec.rotate(self.angle)
        bottomleft = (c[0] + bottomleft_vec.x, c[1] + bottomleft_vec.y)

        bottomright_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        bottomright_vec = bottomright_vec.rotate(self.angle)
        bottomright = (c[0] + bottomright_vec.x, c[1] + bottomright_vec.y)

        return [topleft, topright, bottomright, bottomleft]  
