from .fuzzy_utils import get_triangle_fuzzy_set, get_trapezoid_fuzzy_set, get_labels
from .labels import STEERING_HARD_LEFT, STEERING_LEFT, STEERING_STRAIGHT, STEERING_RIGHT, STEERING_HARD_RIGHT

steering_hard_left = get_trapezoid_fuzzy_set(0, 0, 0.25, 0.4)
steering_left = get_triangle_fuzzy_set(0.25, 0.4, 0.5)
steering_straight = get_triangle_fuzzy_set(0.4, 0.5, 0.6)
steering_right = get_triangle_fuzzy_set(0.5, 0.6, 0.75)
steering_hard_right = get_trapezoid_fuzzy_set(0.6, 0.75, 1, 1)

steering = {
    STEERING_HARD_LEFT: steering_hard_left,
    STEERING_LEFT: steering_left,
    STEERING_STRAIGHT: steering_straight,
    STEERING_RIGHT: steering_right,
    STEERING_HARD_RIGHT: steering_hard_right
}


def get_steering_labels(x):
    return get_labels(x, steering)
