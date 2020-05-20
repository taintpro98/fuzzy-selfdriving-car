import pandas as pd
import numpy as np


class SteeringRules:
    def __init__(
            self,
            df: pd.DataFrame,
            deviation_col='deviation',
            steering_col='steering'
    ):
        self.df = df
        self.deviation_col = deviation_col
        self.steering_col = steering_col

    def find_rules(self, deviation_labels):
        indices = np.where(
            self.df[self.deviation_col].isin(deviation_labels)
        )

        predicates = self.df[[self.deviation_col]].iloc[indices].to_dict(orient='record')
        steering = self.df[self.steering_col].iloc[indices].values

        return list(zip(predicates, steering))
