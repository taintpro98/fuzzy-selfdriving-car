import pygame
from pygame.sprite import Sprite
import os


class Car(Sprite):
    def __init__(self, image_path):
        super(Car, self).__init__()
        original_image = pygame.image.load(os.path.join(image_path)).convert_alpha()
        self.original_image = pygame.transform.rotozoom(original_image, 0, 0.08)
        self.image = self.original_image
        self.rect = self.image.get_rect()

        self.steering = 0
        self.velocity = 0

        print('image: {}, rect: {}, center:{}'.format(self.image, self.rect, self.rect.center))

    def set_position(self, x, y, angle):
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.image, _ = self.rotation(image=self.original_image, rect=self.rect, degree=angle)
        print('rotated_image: {}, rot_rect: {}, old_center:{}'.format(self.image, self.rect, self.rect.center))

    # def turn_left(self):
    #     self.angle += 5
    #     self.image, _ = self.rotation(image=self.image, rect=self.rect, degree=angle)

    # def turn_right(self):
    #     self.angle -= 5
    #     self.image, _ = self.rotation(image=self.image, rect=self.rect, degree=angle)

    @staticmethod
    def rotation(image, rect, degree):
        # Calculate rotated graphics & centre position
        surf = pygame.Surface((48, 23))
        rotated_image = pygame.transform.rotate(image, degree)
        old_center = rect.center
        rotated_surf = pygame.transform.rotate(surf, degree)
        rot_rect = rotated_surf.get_rect()
        rot_rect.center = old_center
        return rotated_image, rot_rect

    def update(self, dt):
        self.image, _ = self.rotation(image=self.original_image, rect=self.rect, degree=self.angle)

