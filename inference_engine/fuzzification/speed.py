from .fuzzy_utils import get_trapezoid_fuzzy_set, get_triangle_fuzzy_set, get_labels
from .labels import SPEED_STOP, SPEED_SLOWER, SPEED_SLOW, SPEED_MEDIUM

stop = get_triangle_fuzzy_set(0, 0, 0.05)
slower = get_triangle_fuzzy_set(0.025, 0.25, 0.525)
slow = get_triangle_fuzzy_set(0.3, 0.6, 0.8)
medium = get_trapezoid_fuzzy_set(0.7, 0.9, 1.0, 1.0)

speed = {
    SPEED_STOP: stop,
    SPEED_SLOWER: slower,
    SPEED_SLOW: slow,
    SPEED_MEDIUM: medium
}


def get_speed_labels(x):
    return get_labels(x, speed)
