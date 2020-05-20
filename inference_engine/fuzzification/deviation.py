from .fuzzy_utils import get_trapezoid_fuzzy_set, get_triangle_fuzzy_set, get_labels
from .labels import DEVIATION_FAR_LEFT, DEVIATION_FAR_RIGHT, DEVIATION_LEFT, DEVIATION_MIDDLE, DEVIATION_RIGHT

deviation_far_left = get_trapezoid_fuzzy_set(0, 0, 0.25, 0.4)
deviation_left = get_triangle_fuzzy_set(0.25, 0.4, 0.5)
deviation_middle = get_triangle_fuzzy_set(0.4, 0.5, 0.6)
deviation_right = get_triangle_fuzzy_set(0.5, 0.6, 0.75)
deviation_far_right = get_trapezoid_fuzzy_set(0.6, 0.75, 1, 1)

deviation = {
    DEVIATION_FAR_LEFT: deviation_far_left,
    DEVIATION_LEFT: deviation_left,
    DEVIATION_MIDDLE: deviation_middle,
    DEVIATION_RIGHT: deviation_right,
    DEVIATION_FAR_RIGHT: deviation_far_right
}


def get_deviation_labels(x):
    return get_labels(x, deviation)