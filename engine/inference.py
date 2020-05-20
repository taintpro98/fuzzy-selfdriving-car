import pandas as pd
import numpy as np
from scipy.integrate import quad

from .steering_rules import SteeringRules

from .fuzzification.deviation import get_deviation_labels
from .fuzzification.steering import get_steering_labels, steering


class InferenceEngine:
    def __init__(self, speed_rules_fn, steering_rules_fn, sep=','):
        self.speed_rules_df = pd.read_csv(speed_rules_fn, sep=sep)
        self.steering_rules_df = pd.read_csv(steering_rules_fn, sep=sep)

        self.steering_rules = SteeringRules(
            self.steering_rules_df,
            deviation_col='deviation',
            steering_col='steering'
        )

    def inference_steering(self, deviation):
        deviation_labels = get_deviation_labels(deviation)

        rules = self.steering_rules.find_rules(deviation_labels)
        combinations = []

        for factors, steering_label in rules:
            weight = deviation_labels[factors['deviation']]

            steering_fuzzy_set = steering[steering_label]

            de_fuzzy_value = (
                quad(lambda x: np.sqrt(min(weight, steering_fuzzy_set(x))) * x, 0, 1)[0]
                / quad(lambda x: np.sqrt(min(weight, steering_fuzzy_set(x))), 0, 1)[0]
            )

            combinations.append((de_fuzzy_value, weight))

        combinations = np.array(combinations)
        return np.sum(combinations[:, 0] * combinations[:, 1]) / np.sum(combinations[:, 1])

