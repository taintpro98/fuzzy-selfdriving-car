from utils import read_rules
from inference_engine.inference_engine import InferenceEngine

# a = 0.7
# print(get_labels(a, deviation))
# print(get_labels(a, light_status))
# print(get_labels(a, steering))
# print(get_labels(a, speed))

speed_inference_engine = InferenceEngine(
    'inference_engine/rules/data/speed_rules.csv',
    'inference_engine/rules/data/steering.csv',
    ','
)

a = speed_inference_engine.inference_speed(
    deviation=0.2,
    distance_light=0.2,
    distance_obstacle=0.7,
    light_status=0.2
)

b = speed_inference_engine.inference_steering(
    deviation=0.2
)

print(a, b)
