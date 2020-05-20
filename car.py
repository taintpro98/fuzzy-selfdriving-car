import pygame
from pygame.sprite import Sprite
import os
import math
from pygame.math import Vector2
from shapely.geometry import Point, Polygon
from settings import DISTANCE_LIGHT_LIMIT, DISTANCE_OBSTACLE_LIMIT

class Car(Sprite):
    def __init__(self, image_path):
        super(Car, self).__init__()
        original_image = pygame.image.load(os.path.join(image_path)).convert_alpha()
        self.original_image = pygame.transform.rotozoom(original_image, 0, 0.025)
        self.width = self.original_image.get_rect().width
        self.height = self.original_image.get_rect().height
        self.scout_vec = Vector2(10, 0)
        self.speed = 0
        self.steering = 0
        self.display = False
        self.left_side = None
        self.right_side = None
        
    def init_position(self, pos, angle):
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.angle = angle
        self.direction = Vector2(1, 0)  # A unit vector pointing rightward.
        self.direction.rotate_ip(angle)
        self.display = True

    def update(self, dt):
        if self.steering != 0:
            # Rotate the direction vector and then the image.
            self.direction.rotate_ip(self.steering)
            self.angle += self.steering
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        # Update the position vector and the rect.
        self.position += self.direction * self.speed
        self.rect.center = self.position
        self.topleft, self.topright, self.bottomright, self.bottomleft = self.get_polygon()
        self.polygon = Polygon([self.topleft, self.topright, self.bottomright, self.bottomleft])
        # print('steering', self.steering)

    def get_polygon(self):
        c = self.rect.center

        topleft_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        topleft_vec = topleft_vec.rotate(self.angle)
        topleft = (c[0] + topleft_vec.x, c[1] + topleft_vec.y)

        topright_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        topright_vec = topright_vec.rotate(self.angle)
        topright = (c[0] + topright_vec.x, c[1] + topright_vec.y)

        bottomleft_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2)
        bottomleft_vec = bottomleft_vec.rotate(self.angle)
        bottomleft = (c[0] + bottomleft_vec.x, c[1] + bottomleft_vec.y)

        bottomright_vec = pygame.math.Vector2(-self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2)
        bottomright_vec = bottomright_vec.rotate(self.angle)
        bottomright = (c[0] + bottomright_vec.x, c[1] + bottomright_vec.y)

        scoutleft_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, -self.height / 2) + self.scout_vec
        scoutleft_vec = scoutleft_vec.rotate(self.angle)
        self.scoutleft = (c[0] + scoutleft_vec.x, c[1] + scoutleft_vec.y)

        scoutright_vec = pygame.math.Vector2(self.width / 2, 0) + pygame.math.Vector2(0, self.height / 2) + self.scout_vec
        scoutright_vec = scoutright_vec.rotate(self.angle)
        self.scoutright = (c[0] + scoutright_vec.x, c[1] + scoutright_vec.y)

        return [topleft, topright, bottomright, bottomleft] 

    # def get_obstacle_distance(self):
    #     if len(self.obstacles) > 0:
    #         obstacle = self.obstacles[0]
    #         distance = self.polygon.distance(obstacle.polygon)

    #         if distance < 0.1:
    #             self.obstacles.pop(0)

    #     obstacles = [obstacle for obstacle in self.obstacles if obstacle.display]
    #     if len(obstacles) > 0:
    #         obstacle = obstacles[0]
    #         distance = self.polygon.distance(obstacle.polygon)

    #         return None if distance > DISTANCE_OBSTACLE_LIMIT else distance / DISTANCE_OBSTACLE_LIMIT
    #     return None

    def get_deviation(self):
        dl = Point(self.topleft).distance(self.left_side)
        dr = Point(self.topright).distance(self.right_side)
        return dl / (dl + dr)

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

    def get_light_status(self):
        if len(self.traffic_lights) > 0:
            traffic_light = self.traffic_lights[0]
            return traffic_light.get_light_status()
        return None

    def get_variables(self):
        # light_distance = self.get_light_distance()
        # obstacle_distance = self.get_obstacle_distance()
        deviation = self.get_deviation()
        # light_status = None if light_distance is None else self.get_light_status()

        # if obstacle_distance and light_distance and (
        #         obstacle_distance < light_distance
        # ):
            # light_distance = None
            # light_status = None
        return {
            # 'distance_light': light_distance,
            # 'distance_obstacle': obstacle_distance,
            'deviation': deviation,
            # 'light_status': light_status
        }
