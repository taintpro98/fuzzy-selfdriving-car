from .fuzzy_utils import get_trapezoid_fuzzy_set, get_labels
from .labels import DISTANCE_OBSTACLE_FAR, DISTANCE_OBSTACLE_MEDIUM, DISTANCE_OBSTACLE_NEAR

near = get_trapezoid_fuzzy_set(0., 0., 0.05, 0.2)
medium = get_trapezoid_fuzzy_set(0.05, 0.1, 0.25, 0.35)
far = get_trapezoid_fuzzy_set(0.2, 0.35, 1, 1)

distance_obstacle = {
    DISTANCE_OBSTACLE_NEAR: near,
    DISTANCE_OBSTACLE_MEDIUM: medium,
    DISTANCE_OBSTACLE_FAR: far
}


def get_distance_obstacle_labels(x):
    return get_labels(x, distance_obstacle)
