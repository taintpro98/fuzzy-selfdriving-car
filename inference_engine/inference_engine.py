import pandas as pd
import numpy as np
from scipy.integrate import quad

from .fuzzification.deviation import get_deviation_labels
from .fuzzification.light_status import get_light_status_labels
from .fuzzification.steering import get_steering_labels, steering
from .fuzzification.distance_obstacle import get_distance_obstacle_labels
from .fuzzification.distance_light import get_distance_light_labels
from .fuzzification.speed import get_speed_labels, speed
from .fuzzification.labels import *

from .rules.speed_rules import SpeedRules
from .rules.steering_rules import SteeringRules

DEVIATION = 'deviation'
DISTANCE_LIGHT = 'distance_light'
DISTANCE_OBSTACLE = 'distance_obstacle'
LIGHT_STATUS = 'light_status'
STEERING = 'steering'
SPEED = 'speed'


class InferenceEngine:
    def __init__(
            self,
            speed_rules_fn,
            steering_rules_fn,
            sep=','
    ):
        self.speed_rules_df = pd.read_csv(speed_rules_fn, sep=sep)
        self.steering_rules_df = pd.read_csv(steering_rules_fn, sep=sep)

        self.speed_rules = SpeedRules(
            self.speed_rules_df,
            deviation_col=DEVIATION,
            distance_light_col=DISTANCE_LIGHT,
            distance_obstacle_col=DISTANCE_OBSTACLE,
            light_status_col=LIGHT_STATUS,
            speed_col=SPEED
        )

        self.steering_rules = SteeringRules(
            self.steering_rules_df,
            deviation_col=DEVIATION,
            steering_col=STEERING
        )

    def inference_speed(self, deviation, light_status, distance_light, distance_obstacle):
        deviation_labels = get_deviation_labels(deviation)
        light_status_labels = get_light_status_labels(light_status) if light_status else {}
        distance_light_labels = get_distance_light_labels(distance_light) if distance_light else {}
        distance_obstacle_labels = get_distance_obstacle_labels(distance_obstacle) if distance_obstacle else {}

        labels = {
            DEVIATION: deviation_labels,
            LIGHT_STATUS: light_status_labels,
            DISTANCE_LIGHT: distance_light_labels,
            DISTANCE_OBSTACLE: distance_obstacle_labels
        }

        rules = self.speed_rules.find_rules(
            distance_obstacle_labels=list(distance_obstacle_labels.keys()),
            distance_light_labels=list(distance_light_labels.keys()),
            deviation_labels=list(deviation_labels.keys()),
            light_status_labels=list(light_status_labels.keys())
        )
        if len(rules) == 0:
            return None

        combinations = []

        for factors, speed_label in rules:
            weights = [labels[factor][label] for factor, label in factors.items()]
            min_weight = min(weights)
            importance = np.prod(weights)

            speed_fuzzy_set = speed[speed_label]

            de_fuzzy_value = (
                quad(lambda x: np.sqrt(min(min_weight, speed_fuzzy_set(x))) * x, 0, 1)[0]
                / quad(lambda x: np.sqrt(min(min_weight, speed_fuzzy_set(x))), 0, 1)[0]
            )

            combinations.append((de_fuzzy_value, importance))

        combinations = np.array(combinations)

        return np.sum(combinations[:, 0] * combinations[:, 1]) / np.sum(combinations[:, 1])

    def inference_steering(self, deviation):
        deviation_labels = get_deviation_labels(deviation)

        rules = self.steering_rules.find_rules(deviation_labels)
        combinations = []

        for factors, steering_label in rules:
            weight = deviation_labels[factors[DEVIATION]]

            steering_fuzzy_set = steering[steering_label]

            de_fuzzy_value = (
                quad(lambda x: np.sqrt(min(weight, steering_fuzzy_set(x))) * x, 0, 1)[0]
                / quad(lambda x: np.sqrt(min(weight, steering_fuzzy_set(x))), 0, 1)[0]
            )

            combinations.append((de_fuzzy_value, weight))

        combinations = np.array(combinations)
        return np.sum(combinations[:, 0] * combinations[:, 1]) / np.sum(combinations[:, 1])
