import pandas as pd
import numpy as np


class SpeedRules:
    def __init__(
            self,
            df: pd.DataFrame,
            distance_obstacle_col='distance_obstacle',
            light_status_col='light_status',
            distance_light_col='distance_light',
            deviation_col='deviation',
            speed_col='speed'
    ):
        self.df = df
        self.distance_obstacle_col = distance_obstacle_col
        self.light_status_col = light_status_col
        self.distance_light_col = distance_light_col
        self.deviation_col = deviation_col
        self.speed_col = speed_col

    def find_rules(
            self,
            distance_obstacle_labels,
            light_status_labels,
            distance_light_labels,
            deviation_labels
    ):
        indices = np.where(
            self.df[self.distance_obstacle_col].isin([*distance_obstacle_labels, np.nan])
            & self.df[self.light_status_col].isin([*light_status_labels, np.nan])
            & self.df[self.distance_light_col].isin([*distance_light_labels, np.nan])
            & self.df[self.deviation_col].isin([*deviation_labels, np.nan])
        )

        predicates = self.df[[
            self.distance_obstacle_col,
            self.distance_light_col,
            self.light_status_col,
            self.deviation_col
        ]].iloc[indices]

        predicates = [value.dropna().to_dict() for key, value in predicates.iterrows()]
        speeds = self.df[self.speed_col].iloc[indices].values
        return list(zip(predicates, speeds))
