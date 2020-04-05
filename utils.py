import pygame

def init_screen(w, h):
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    return screen