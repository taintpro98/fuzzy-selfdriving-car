import os.path
import warnings

import pygame
from pygame.locals import *
from pygame import mouse
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

from shapely.geometry import LineString, Point, Polygon

import utils
from settings import *
from car import Car
from map import Map
from traffic_light import TrafficLight
from obstacle import Obstacle
from inference_engine.inference_engine import InferenceEngine

warnings.filterwarnings('ignore')


class Game:
    file_name = utils.get_map(MAP_FILENAME)

    def __init__(self):
        self.inference_engine = InferenceEngine(
            speed_rules_fn='inference_engine/rules/data/speed_rules.csv',
            steering_rules_fn='inference_engine/rules/data/steering.csv',
            sep=','
        )
        self.running = False

        # self.tmx_data = load_pygame(self.file_name)
        self.tmx_data = load_pygame('map/map.tmx')
        self.start_end = []
        self.font = pygame.font.Font('freesansbold.ttf', 32)

        self.map = Map(tmx_data=self.tmx_data)

        self.traffic_light_positions = None
        self.traffic_lights = []

        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=True)
        self.map_layer.zoom = 0.3
        self.zoomchange = 1

        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

        self.car = Car('car.png')
        self.obstacles = []

        self.path = None
        self.path_sides = None
        self.left_side_line_string = None
        self.right_side_line_string = None
        self.obstacle_positions = None
        self.finish_point = None

        self.focus_car = False

        self.start = False
        self.finished = False

    def draw(self, surface):
        if self.focus_car:
            self.group.center(self.car.rect.center)
        self.group.draw(surface)

    def handle_click(self):
        poll = pygame.event.poll
        event = poll()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_position_in_map = self.convert_screen_coordinate_2_map_coordinate(*mouse.get_pos())
            node, coordinate = self.map.get_nearest_node_in_graph(*mouse_position_in_map)
            if len(self.start_end) == 0:
                self.start_end.append((node, coordinate))
            if len(self.start_end) == 1 and node != self.start_end[0][0]:
                self.start_end.append((node, coordinate))

                (
                    self.path,
                    self.path_sides,
                    self.traffic_light_positions,
                    self.obstacle_positions
                ) = self.map.get_shortest_path(self.start_end[0][0], self.start_end[1][0])

                self.display_traffic_light()
                # self.display_obstacles(self.obstacle_positions)
                self.left_side_line_string = LineString(coordinates=self.path_sides['left_side_points'])
                self.right_side_line_string = LineString(coordinates=self.path_sides['right_side_points'])
                self.finish_point = self.get_rect_with_point(self.start_end[1][1], bound=16)

                left_start_point = self.path_sides['left_side_points'][0]
                right_start_point = self.path_sides['right_side_points'][0]
                start_point = (
                    (left_start_point[0] + right_start_point[0]) / 2,
                    (left_start_point[1] + right_start_point[1]) / 2
                )
                self.display_car(start_point)
            event = poll()
        elif event.type == QUIT:
            self.running = False

    # def auto_run(self):

    def handle_input(self):
        poll = pygame.event.poll

        event = poll()
        while event:
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break

                elif event.key == K_EQUALS:
                    self.map_layer.zoom += .25

                elif event.key == K_MINUS:
                    value = self.map_layer.zoom - .25
                    if value > 0:
                        self.map_layer.zoom = value

                elif event.key == K_SPACE:
                    if self.left_side_line_string and self.right_side_line_string:
                        self.start = not self.start

            # if event.type = SPACE:

            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                utils.init_screen(event.w, event.h)
                self.map_layer.set_size((event.w, event.h))

            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                mouse_position_in_map = self.convert_screen_coordinate_2_map_coordinate(*mouse.get_pos())
                existed = None
                # for idx, obs in enumerate(self.obstacles):
                #     if obs.rect.collidepoint(mouse_position_in_map):
                #         existed = idx
                #         obstacle = self.obstacles.pop(idx)
                #         self.car.remove_obstacle(obstacle)
                #         obstacle.display = False
                #         del obstacle
                removed = self.car.remove_obstacle_by_point(mouse_position_in_map)
                if not removed:
                    obs = Obstacle(mouse_position_in_map, 'rock1.png')
                    self.obstacles.append(obs)
                    self.car.add_obstacles(obs)
                    self.group.add(obs)
                print(mouse_position_in_map)
            event = poll()

        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            if self.car.velocity[0] < 0:
                self.car.acceleration = brake_deceleration
            else:
                self.car.acceleration += ACCELERATION
        elif pressed[K_DOWN]:
            if self.car.velocity[0] > 0:
                self.car.acceleration = -brake_deceleration
            else:
                self.car.acceleration -= ACCELERATION
        else:
            self.car.acceleration = 0
        self.car.acceleration = max(-self.car.max_acceleration, min(self.car.acceleration, self.car.max_acceleration))

        if pressed[K_LEFT]:
            self.car.steering += 5
        elif pressed[K_RIGHT]:
            self.car.steering -= 5
        else:
            self.car.steering = 0
        self.car.steering = max(-self.car.max_steering, min(self.car.steering, self.car.max_steering))

    def compute_delta_left(self):
        car_polygon = self.car.get_polygon()
        point_left = Point(car_polygon[0])
        return point_left.distance(self.left_side_line_string)

    def compute_delta_right(self):
        car_polygon = self.car.get_polygon()
        point_right = Point(car_polygon[1])
        return point_right.distance(self.right_side_line_string)

    def compute_deviation(self):
        dl = self.compute_delta_left()
        dr = self.compute_delta_right()
        return dl / (dl + dr)

    def display_message(self):
        if len(self.start_end) == 1:
            return f"Start: {self.start_end[0][1]}"
        if len(self.start_end) == 2:
            return "Start: {}, End: {}".format(self.start_end[0][1], self.start_end[1][1])
        return ""

    def update(self, dt):
        """ Tasks that occur over time should be handled here
        """
        self.group.update(dt)

    def get_direction_angle(self):
        path_direction = pygame.math.Vector2(
            self.path_sides['left_side_points'][1][0] - self.path_sides['left_side_points'][0][0],
            self.path_sides['left_side_points'][1][1] - self.path_sides['left_side_points'][0][1])
        car_direction = pygame.math.Vector2(1, 0)
        angle = path_direction.angle_to(car_direction)
        return angle

    def convert_screen_coordinate_2_map_coordinate(self, x, y):
        mx, my = self.map_layer.get_center_offset()
        ratio_x, ratio_y = self.map_layer._real_ratio_x, self.map_layer._real_ratio_y
        map_x = int(x / ratio_x - mx)
        map_y = int(y / ratio_y - my)
        return map_x, map_y

    def display_traffic_light(self):
        for position in self.traffic_light_positions:
            traffic_light = TrafficLight(
                position,
                'traffic_lamp_red.png',
                'traffic_lamp_yellow.png',
                'traffic_lamp_green.png')
            self.traffic_lights.append(traffic_light)

        self.group.add(self.traffic_lights)

    def display_car(self, position):
        self.focus_car = True
        self.zoomchange = 2 / float(self.map_layer.zoom)
        self.map_layer.zoom = 2

        angle = self.get_direction_angle()
        self.car.position = position
        self.car.angle = angle

        self.car.traffic_lights.extend(self.traffic_lights)
        self.car.left_side = self.left_side_line_string
        self.car.right_side = self.right_side_line_string

        self.group.add(self.car)

    def display_obstacles(self, positions):
        obstacles = [Obstacle(position, 'rock1.png') for position in positions]
        self.obstacles.extend(obstacles)
        self.car.obstacles.extend(obstacles)
        # self.car.update_obstacles()
        self.group.add(obstacles)

    # def show_obstacle(self, position):

    @staticmethod
    def get_rect_with_point(point, bound=16):
        print(point)
        x, y = point
        max_x, max_y, min_x, min_y = x + bound, y + bound, x - bound, y - bound

        return Polygon([(max_x, max_y), (max_x, min_y), (min_x, min_y), (min_x, max_y)])

    def run(self):
        clock = pygame.time.Clock()
        self.running = True
        from collections import deque
        times = deque(maxlen=FPS)

        try:
            while self.running:

                dt = clock.tick(FPS) / 1000.
                times.append(clock.get_fps())

                if len(self.start_end) < 2:
                    self.handle_click()
                self.handle_input()

                if self.start and not self.finished:
                    if not self.car.polygon.intersection(self.finish_point):
                        variables = self.car.get_variables()

                        speed = self.inference_engine.inference_speed(**variables)
                        steering = self.inference_engine.inference_steering(variables['deviation'])
                        steering_angle = (0.5 - steering) * 180 * 1.3
                        if speed:
                            self.car.velocity[0] = speed * self.car.max_speed if speed > 0.1 else 0
                        else:
                            self.car.acceleration += ACCELERATION

                        self.car.steering += steering_angle
                    else:
                        self.finished = True
                        self.car.velocity[0] = 0

                self.update(dt)
                self.draw(screen)

                text = self.font.render(self.display_message(), True, (0, 0, 0))
                text_rect = text.get_rect()
                text_rect.right = 950  # align to right to 150px
                screen.blit(text, text_rect)

                if self.finished:
                    w, h = pygame.display.get_surface().get_size()
                    text = pygame.font.Font('freesansbold.ttf', 80).render('DONE!!!', True, (255, 0, 0))
                    text_rect = text.get_rect()
                    text_rect.right = w / 2 + text_rect.w / 2
                    text_rect.top = h / 2 - text_rect.h / 2
                    screen.blit(text, text_rect)

                if self.path_sides:
                    pygame.draw.lines(
                        screen,
                        Color('blue'),
                        False,
                        self.map_layer.translate_points(self.path_sides['left_side_points']),
                        4
                    )
                    pygame.draw.lines(
                        screen,
                        Color('blue'),
                        False,
                        self.map_layer.translate_points(self.path_sides['right_side_points']),
                        4
                    )

                car_polygon = self.car.get_polygon()
                pygame.draw.lines(
                    screen,
                    Color('red'),
                    True,
                    self.map_layer.translate_points(car_polygon),
                    4
                )

                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = utils.init_screen(950, 950)
    pygame.display.set_caption('Test')

    try:
        game = Game()
        game.run()
    except:
        pygame.quit()
        raise
