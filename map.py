import networkx as nx
import numpy as np
from collections import defaultdict
import re

from shapely.geometry import LineString

class Map:
    def __init__(self, tmx_data, graph_points_layer_name='graph_points', graph_road_points_layer_name='road_points', graph_road_point_props_sep='_',):
        self.tmx_data = tmx_data
        self.graph_points_layer_name = graph_points_layer_name
        self.graph_road_points_layer_name = graph_road_points_layer_name
        self.graph_road_point_props_sep = graph_road_point_props_sep
        self.graph = self.get_graph(tmx_data, graph_points_layer_name, graph_road_points_layer_name, graph_road_point_props_sep)
        (
            self.traffic_light_positions,
            self.traffic_light_between_edges
        ) = self.get_position_of_traffic_lights('traffic_lights')
        # self.obstacle_positions = self.get_position_of_obstacles(tmx_data, 'obstacles')
        # self.smooth_edges_points = self.get_smooth_points(tmx_data, 'smooth_road_points')

    @staticmethod
    def get_distance(node1: tuple, node2: tuple):
        return np.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

    def get_coordinates_of_node(self, node):
        if self.graph.has_node(node):
            attributes = self.graph.nodes[node]
            x, y = attributes['x'], attributes['y']
            return x, y
        return None

    def get_nearest_node_in_graph(self, x, y):
        nearest_node = None
        nearest_coordinate = None
        min_distance = 999999999
        for node in self.graph.nodes:
            node_coordinates = self.get_coordinates_of_node(node)
            distance = self.get_distance(node_coordinates, (x, y))
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
                nearest_coordinate = node_coordinates

        return nearest_node, nearest_coordinate

    def get_traffic_lights(self, path):
        traffic_lights = []

        edges = list(zip(path[:-1], path[1:]))
        for from_edge, to_edge in zip(edges[:-1], edges[1:]):
            traffic_lights.append(self.traffic_light_between_edges.get((from_edge[0], to_edge[0], to_edge[1]), []))

        return traffic_lights

    # def get_obstacles(self, path):
    #     obstacles = []
    #     for from_point, to_point in zip(path[:-1], path[1:]):
    #         obstacles.append(self.obstacle_positions[(from_point, to_point)])
    #     return obstacles

    def get_path_sides(self, path):
        left_side_points = []
        right_side_points = []

        previous_edge = None
        for from_point, to_point in zip(path[:-1], path[1:]):
            if previous_edge:
                smooth_points = self.smooth_edges_points.get((previous_edge[0], from_point, to_point))
                if smooth_points:
                    left_side_points.extend(smooth_points['left_side_points'])
                    right_side_points.extend(smooth_points['right_side_points'])

            edge_data = self.graph.get_edge_data(from_point, to_point)
            left_side_points.extend(edge_data['left_side_points'])
            right_side_points.extend(edge_data['right_side_points'])
            previous_edge = from_point, to_point

        return {
            'left_side_points': left_side_points,
            'right_side_points': right_side_points
        }

    def get_shortest_path(self, from_node, to_node):
        path = nx.shortest_path(self.graph, from_node, to_node)
        return path, self.get_path_sides(path), self.get_traffic_lights(path), None

    @staticmethod
    def get_graph(
            tmx_data,
            graph_points_layer_name,
            graph_road_points_layer_name,
            graph_road_point_props_sep
    ):
        # get nodes
        nodes = []

        graph_points_layer = tmx_data.get_layer_by_name(graph_points_layer_name)
        for point in graph_points_layer:
            nodes.append((point.name, {'x': point.x, 'y': point.y}))
        # get edges
        map_road_side_points = defaultdict(dict)
        road_points_layer = tmx_data.get_layer_by_name(graph_road_points_layer_name)

        for point in road_points_layer:
            name = point.name
            source, destination, side, order = re.split(fr'{graph_road_point_props_sep}+', name)
            side_points = map_road_side_points[(source, destination)].setdefault(side, [])
            side_points.append(((point.x, point.y), int(order)))

        # get edges
        graph_edges = list()

        for (source, destination), sides in map_road_side_points.items():
            left_side_points = [(x, y) for (x, y), order in sorted(sides['l'], key=lambda x: x[1])]
            right_side_points = [(x, y) for (x, y), order in sorted(sides['r'], key=lambda x: x[1])]
            weight = (LineString(left_side_points).length + LineString(right_side_points).length) / 2

            graph_edges.append((f'point_{source}', f'point_{destination}', {
                'left_side_points': left_side_points,
                'right_side_points': right_side_points,
                'weight': weight
            }))

            graph_edges.append((f'point_{destination}', f'point_{source}', {
                'left_side_points': right_side_points[::-1],
                'right_side_points': left_side_points[::-1],
                'weight': weight
            }))

        graph = nx.DiGraph()

        # add nodes to graph
        for node in nodes:
            graph.add_node(node[0], **node[1])

        graph.add_edges_from(graph_edges)
        return graph

    def get_position_of_traffic_lights(self, traffic_light_layer_name='traffic_lights'):
        traffic_light_layer = self.tmx_data.get_layer_by_name(traffic_light_layer_name)
        positions = []
        map_edges_traffic_light = {}
        for traffic_light in traffic_light_layer:
            position = traffic_light.x, traffic_light.y
            between = re.split(r',', traffic_light.properties['between'])

            for light in between:
                source, through, destination = re.split(r'_', light)
                map_edges_traffic_light[(f'point_{source}', f'point_{through}', f'point_{destination}')] = position

            positions.append(position)

        return positions, map_edges_traffic_light

    @staticmethod
    def get_smooth_points(
            tmx_data,
            smooth_points_layer_name='smooth_road_points'
    ):
        # smooth road points
        road_smooth_points = defaultdict(dict)
        smooth_road_points_layer = tmx_data.get_layer_by_name(smooth_points_layer_name)

        for point in smooth_road_points_layer:
            name = point.name
            source, through, destination, side, order = re.split(r'_', name)
            smooth_side_points = road_smooth_points[(source, through, destination)].setdefault(side, [])
            smooth_side_points.append(((point.x, point.y), int(order)))

        smooth_edges_points = dict()

        for (source, through, destination), sides in road_smooth_points.items():
            left_side_points = [(x, y) for (x, y), order in sorted(sides.get('l', []), key=lambda x: x[1])]
            right_side_points = [(x, y) for (x, y), order in sorted(sides.get('r', []), key=lambda x: x[1])]

            smooth_edges_points[(f'point_{source}', f'point_{through}', f'point_{destination}')] = {
                'left_side_points': left_side_points,
                'right_side_points': right_side_points
            }

            smooth_edges_points[(f'point_{destination}', f'point_{through}', f'point_{source}')] = {
                'left_side_points': right_side_points[::-1],
                'right_side_points': left_side_points[::-1]
            }
        return smooth_edges_points
