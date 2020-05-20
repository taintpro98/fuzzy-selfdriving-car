import pygame
import os
from settings import *

def init_screen(w, h):
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    return screen

def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))