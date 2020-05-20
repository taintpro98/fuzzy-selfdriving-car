from settings import *
import pygame
import os
import math
import numpy as np
import pandas as pd


def init_screen(width, height):
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen


def get_map(filename):
    return os.path.join(RESOURCES_DIR, filename)


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))


def unit_vector(vector):
    vector = np.array(vector)
    return vector / np.linalg.norm(vector)


def angle_x(vector):
    if vector[0] == 0 and vector[1] != 0:
        angle = - np.pi / 2 if vector[1] < 0 else np.pi / 2
    elif vector[1] == 0:
        angle = 0
    else:
        tan = vector[1] / vector[0]
        angle = np.arctan(tan)
    return angle


def rot_center(image, rect, angle):
    """rotate an image while keeping itscenter"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


def read_rules(fn, sep=','):
    df = pd.read_csv(fn, sep=sep)
    predicates = [value.dropna().to_dict() for key, value in df.iloc[:, :-1].iterrows()]
    targets = df.iloc[:, -1].values

    return list(zip(predicates, targets))
