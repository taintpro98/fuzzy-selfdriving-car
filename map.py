import networkx as nx
import numpy as np
from collections import defaultdict
import re

from shapely.geometry import LineString

class Map:
    def __init__(self, tmx_data):
        self.tmx_data = tmx_data
