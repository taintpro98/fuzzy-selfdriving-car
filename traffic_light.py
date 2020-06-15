from pygame.sprite import Sprite
import pygame
import random

import utils
from settings import FPS

YELLOW_SECOND, SUM_SECOND = 6, 10


class TrafficLight(Sprite):
    def __init__(
            self,
            position,
            red_img_path,
            yellow_img_path,
            green_img_path
    ):
        super(TrafficLight, self).__init__()
        self.red_img = pygame.transform.rotozoom(utils.load_image(red_img_path).convert_alpha(), 0, 1)
        self.yellow_img = pygame.transform.rotozoom(utils.load_image(yellow_img_path).convert_alpha(), 0, 1)
        self.green_img = pygame.transform.rotozoom(utils.load_image(green_img_path).convert_alpha(), 0, 1)
        self.second = random.randint(0, SUM_SECOND)

        self._position = position
        self.no_frames = 0
        self.image = self.get_display_image()

        self.rect = self.image.get_rect()
        self.rect.center = self._position

        self.width = self.rect.width
        self.height = self.rect.height

        self.font = pygame.font.SysFont("Arial", 32, bold=True)

    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    def get_display_image(self):
        if self.second < YELLOW_SECOND:
            return self.green_img
        elif self.second == YELLOW_SECOND:
            return self.yellow_img
        else:
            return self.red_img

    def update(self, dt):
        self.no_frames = (self.no_frames + 1) % FPS
        if self.no_frames == 0:
            self.second = (self.second + 1) % SUM_SECOND
        display_image = self.get_display_image()

        text = self.font.render(
            str(SUM_SECOND - self.second if self.second > YELLOW_SECOND else YELLOW_SECOND - self.second),
            True,
            (0, 0, 0)
        )
        text_width = text.get_width()
        text_height = text.get_height()

        self.image = pygame.Surface((self.width + text_width, self.height + text_height), pygame.SRCALPHA, 32)
        self.image.blit(display_image, [0, 0])
        self.image.blit(text, [self.width, self.height / 2 - text_width / 2])

    # def update(self, dt):
    #     display_image = self.get_display_image()
    #     for e in pygame.event.get():
            
    #         if e.type == pygame.USEREVENT:
    #             self.second = (self.second + 1) % SUM_SECOND
    #         if e.type == pygame.QUIT: break
    #     else:
    #         text = self.font.render(
    #             str(SUM_SECOND - self.second if self.second > YELLOW_SECOND else YELLOW_SECOND - self.second),
    #             True,
    #             (0, 0, 0)
    #         )
    #         text_width = text.get_width()
    #         text_height = text.get_height()
    #         self.image = pygame.Surface((self.width + text_width, self.height + text_height), pygame.SRCALPHA, 32)
    #         self.image.blit(display_image, [0, 0])
    #         self.image.blit(text, [self.width, self.height / 2 - text_width / 2])
            

    def get_light_status(self):
        return self.second / SUM_SECOND
