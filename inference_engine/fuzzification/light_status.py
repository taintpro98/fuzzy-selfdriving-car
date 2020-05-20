from .fuzzy_utils import get_trapezoid_fuzzy_set, get_triangle_fuzzy_set, get_labels
from .labels import (
    LIGHT_STATUS_GREEN, LIGHT_STATUS_LESS_GREEN, LIGHT_STATUS_YELLOW, LIGHT_STATUS_LESS_RED, LIGHT_STATUS_RED
)

green = get_trapezoid_fuzzy_set(0, 0, 0.25, 0.4)
less_green = get_triangle_fuzzy_set(0.32, 0.42, 0.54)
yellow = get_triangle_fuzzy_set(0.44, 0.54, 0.72)
red = get_trapezoid_fuzzy_set(0.62, 0.66, 0.82, 0.9)
less_red = get_trapezoid_fuzzy_set(0.83, 0.92, 1, 1)

light_status = {
    LIGHT_STATUS_GREEN: green,
    LIGHT_STATUS_LESS_GREEN: less_green,
    LIGHT_STATUS_YELLOW: yellow,
    LIGHT_STATUS_LESS_RED: less_red,
    LIGHT_STATUS_RED: red
}


def get_light_status_labels(x):
    return get_labels(x, light_status)
