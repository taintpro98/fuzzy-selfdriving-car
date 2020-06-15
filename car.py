from pygame.sprite import Sprite
import pygame
import math
from shapely.geometry import Point, Polygon

import utils

DISTANCE_LIGHT_LIMIT = 300
DISTANCE_OBSTACLE_LIMIT = 100


class Car(Sprite):
    min_speed = -50
    max_speed = 200
    min_acceleration = 0
    max_acceleration = 50
    max_steering = 45

    def __init__(self, image_path):
        super(Car, self).__init__()
        self.original_image = pygame.transform.rotozoom(utils.load_image(image_path).convert_alpha(), 0, 0.10)
        # self.image = self.original_image
        self.velocity = [0, 0]
        self._position = [0, 0]
        self._old_position = self.position
        # self.rect = self.image.get_rect()
        # self.width = self.rect.width
        # self.height = self.rect.height
        self.width = self.original_image.get_rect().width
        self.height = self.original_image.get_rect().height

        self.direction = [1, 0]
        self.acceleration = 0
        self.angle = 0
        # self.brake_deceleration = 10
        self.steering = 0
        self.traffic_lights = []
        self.obstacles = []
        self.obstacles_unsorted = []
        self.polygon = None
        self.left_side = None
        self.right_side = None
        self.topleft, self.topright, self.bottomright, self.bottomleft = None, None, None, None
        self.previous_distance_light = 999999999

    def init_position(self, position, angle):
        self.image = self.original_image
        self.rect = self.image.get_rect(center=position)
        self.position = position
        self.angle = angle

    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)
        # self.rect = pygame.Rect((value[0] - self.height / 2, value[1] - self.width / 2),
        #                         (self.width , self.height))
        # self.angle = value[1]

    def get_polygon(self):
        topleft_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        topleft_vec = topleft_vec.rotate(-self.angle)
        topleft = (self._position[0] + topleft_vec.x, self._position[1] + topleft_vec.y)

        topright_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        topright_vec = topright_vec.rotate(-self.angle)
        topright = (self._position[0] + topright_vec.x, self._position[1] + topright_vec.y)

        bottomleft_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        bottomleft_vec = bottomleft_vec.rotate(-self.angle)
        bottomleft = (self._position[0] + bottomleft_vec.x, self._position[1] + bottomleft_vec.y)

        bottomright_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        bottomright_vec = bottomright_vec.rotate(-self.angle)
        bottomright = (self._position[0] + bottomright_vec.x, self._position[1] + bottomright_vec.y)

        poly = [topleft, topright, bottomright, bottomleft]
        return poly

    def update(self, dt):
        self._old_position = self.position[:]
        old_velocity = self.velocity.copy()
        self.update_velocity(dt)

        angle = self.angle
        self.image, self.rect, old_center = self.rotation(image=self.original_image, rect=self.rect, degree=angle)

        self._position = self.get_update_position(self._position, dt)
        self.rect.center = self._position
        self.topleft, self.topright, self.bottomright, self.bottomleft = self.get_polygon()
        self.polygon = Polygon([self.topleft, self.topright, self.bottomright, self.bottomleft])
        # print('topleft', self.bottomleft)
        # print('top left car', self.rect.x - self.rect.width/2)

    def update_velocity(self, dt):
        v0 = self.velocity[0] + self.acceleration * dt
        v1 = self.velocity[1] + 0

        if self.min_speed <= v0 <= self.max_speed:
            self.velocity[0] = v0
        elif v0 < self.min_speed:
            self.velocity[0] = self.min_speed
        else:
            self.velocity[0] = self.max_speed

        if self.min_speed <= v1 <= self.max_speed:
            self.velocity[1] = v1
        elif v1 < self.min_speed:
            self.velocity[1] = self.min_speed
        else:
            self.velocity[1] = self.max_speed

    def get_update_position(self, point, dt, ontic=True):
        pos = pygame.math.Vector2(point[0], point[1])
        vel = pygame.math.Vector2(self.velocity[0], self.velocity[1])
        if self.steering:
            turning_radius = self.width / math.sin(math.radians(self.steering))
            angular_velocity = vel.x / turning_radius
        else:
            angular_velocity = 0
        new_pos = pos + vel.rotate(-self.angle) * dt
        if ontic:
            self.angle += math.degrees(angular_velocity) * dt
        return [new_pos.x, new_pos.y]

    def steer(self, value, dt):
        self.steering += value * dt

    def move_back(self, dt):
        self._position = self._old_position
        self.rect.topleft = self._position

    @staticmethod
    def rotation(image, rect, degree):
        # Calculate rotated graphics & centre position
        surf = pygame.Surface((48, 23))
        rotated_image = pygame.transform.rotate(image, degree)
        old_center = rect.center
        rotated_surf = pygame.transform.rotate(surf, degree)
        rot_rect = rotated_surf.get_rect()
        rot_rect.center = old_center
        return rotated_image, rot_rect, old_center

    def get_light_distance(self):
        if len(self.traffic_lights) > 0:
            traffic_light = self.traffic_lights[0]
            distance = Point(traffic_light.position).distance(self.polygon)

            if distance < 0.1:
                self.traffic_lights.pop(0)
                if len(self.traffic_lights) == 0:
                    return 1
                else:
                    traffic_light = self.traffic_lights[0]
                    distance = Point(traffic_light.position).distance(self.polygon)

            return None if distance > DISTANCE_LIGHT_LIMIT else distance / DISTANCE_LIGHT_LIMIT

        return None

    def add_traffic_lights(self, traffic_lights):
        self.traffic_lights.extend(traffic_lights)

    def add_obstacles(self, obstacles):
        obstacles = self.obstacles + [obstacles]
        # self.obstacles_unsorted = obstacles
        self.obstacles = sorted(obstacles, key=lambda obstacle: self.polygon.distance(obstacle.polygon))

    def remove_obstacle_by_point(self, point):
        remove_obstacles = []
        for i, obs in enumerate(self.obstacles):
            if obs.rect.collidepoint(point):
                obs.display = False
                remove_obstacles.append(obs)
        # self.obstacles = sorted([obstacle for i, obstacle in enumerate(self.obstacles) if obstacle])
        for obs in remove_obstacles:
            self.obstacles.remove(obs)

        return len(remove_obstacles) > 0

    def get_obstacle_distance(self):
        if len(self.obstacles) > 0:
            obstacle = self.obstacles[0]
            distance = self.polygon.distance(obstacle.polygon)

            if distance < 0.1:
                self.obstacles.pop(0)

        obstacles = [obstacle for obstacle in self.obstacles if obstacle.display]
        if len(obstacles) > 0:
            obstacle = obstacles[0]
            distance = self.polygon.distance(obstacle.polygon)

            return None if distance > DISTANCE_OBSTACLE_LIMIT else distance / DISTANCE_OBSTACLE_LIMIT
        return None

    def get_deviation(self):
        dl = Point(self.topleft).distance(self.left_side)
        dr = Point(self.topright).distance(self.right_side)
        return dl / (dl + dr)

    def get_light_status(self):
        if len(self.traffic_lights) > 0:
            traffic_light = self.traffic_lights[0]
            return traffic_light.get_light_status()
        return None

    def get_variables(self):
        distance_light = self.get_light_distance()
        distance_obstacle = self.get_obstacle_distance()
        deviation = self.get_deviation()
        light_status = None if distance_light is None else self.get_light_status()
        if distance_obstacle and distance_light and (
                distance_obstacle < distance_light
        ):
            distance_light = None
            light_status = None
        return {
            'distance_light': distance_light,
            'distance_obstacle': distance_obstacle,
            'deviation': deviation,
            'light_status': light_status
        }
