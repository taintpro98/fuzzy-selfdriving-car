from pygame.sprite import Sprite
import pygame
import random
from shapely.geometry import Polygon

import utils
from settings import FPS

SHOW_TIME = 10
HIDDEN_TIME = 5
TOTAL_TIME = SHOW_TIME + HIDDEN_TIME


class Obstacle(pygame.sprite.Sprite):
    def __init__(
            self,
            position,
            image_path
    ):
        super(Obstacle, self).__init__()
        self.original_image = utils.load_image(image_path)
        self.hidden_image = pygame.Surface((2, 2), pygame.SRCALPHA, 32)
        self.image = self.original_image

        self._position = position

        self.rect = self.original_image.get_rect()
        self.rect.center = self._position

        self.show_time_in_sec = random.randint(SHOW_TIME - 3, SHOW_TIME - 2)
        self.no_frames = 0
        self.display = True
        self.polygon = Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])


    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    # def update(self, dt):
    #     # if self.display:
    #     #     self.no_frames = (self.no_frames + 1) % FPS
    #     #     if self.no_frames == 0:
    #     #         self.show_time_in_sec -= 1
    #     #         if self.show_time_in_sec == 0:
    #     #             self.display = False
    #     #             self.image = pygame.Surface((2, 2), pygame.SRCALPHA, 32)
    #     self.no_frames = (self.no_frames + 1) % FPS
    #     if self.no_frames == 0:
    #         self.show_time_in_sec = (self.show_time_in_sec + 1) % TOTAL_TIME
    #         if self.show_time_in_sec < SHOW_TIME:
    #             self.display = True
    #             self.image = self.original_image
    #         else:
    #             self.display = False
    #             self.image = self.hidden_image
    
    def update(self, dt):
        if self.display:
            self.image = self.original_image
        else:
            self.image = self.hidden_image