from .fuzzy_utils import get_trapezoid_fuzzy_set, get_labels
from .labels import DISTANCE_LIGHT_FAR, DISTANCE_LIGHT_MEDIUM, DISTANCE_LIGHT_NEAR

# normalized by division by 200
near = get_trapezoid_fuzzy_set(0., 0., 0.05, 0.2)
medium = get_trapezoid_fuzzy_set(0.05, 0.1, 0.25, 0.35)
far = get_trapezoid_fuzzy_set(0.2, 0.35, 1., 1.)

distance_light = {
    DISTANCE_LIGHT_NEAR: near,
    DISTANCE_LIGHT_MEDIUM: medium,
    DISTANCE_LIGHT_FAR: far
}


def get_distance_light_labels(x):
    return get_labels(x, distance_light)
