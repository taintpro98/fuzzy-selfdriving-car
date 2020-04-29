import pygame, sys
from pygame.locals import *
from pytmx.util_pygame import load_pygame
from map import Map
import pyscroll
from pyscroll.group import PyscrollGroup
import utils
from car import Car
from shapely.geometry import LineString, Point, Polygon


class Game:
    def __init__(self):
        self.running = False
        self.file_name = 'map/map.tmx'
        self.tmx_data = load_pygame(self.file_name)
        self.map = Map(tmx_data=self.tmx_data)
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.focus_car = False
        self.start_end = []
        self.car = Car('mymap/car.png')
        self.path_sides = None

    def init_group(self):
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=True)
        self.map_layer.zoom = 0.3
        self.zoomchange = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

    def update(self, dt):
        self.group.update(dt)

    def get_direction_angle(self):
        path_direction = pygame.math.Vector2(
            self.path_sides['left_side_points'][1][0] - self.path_sides['left_side_points'][0][0],
            self.path_sides['left_side_points'][1][1] - self.path_sides['left_side_points'][0][1])
        car_direction = pygame.math.Vector2(1, 0)
        angle = path_direction.angle_to(car_direction)
        return -angle

    def draw(self, surface):
        if self.focus_car:
            self.group.center(self.car.rect.center)
        self.group.draw(surface)

    def render_car(self, position):
        angle = self.get_direction_angle()
        self.car.init_position(position, angle)
        self.focus_car = True
        self.group.add(self.car)

    def convert_screen_coordinate_2_map_coordinate(self, pos):
        x, y = pos
        mx, my = self.map_layer.get_center_offset()
        ratio_x, ratio_y = self.map_layer._real_ratio_x, self.map_layer._real_ratio_y
        map_x = int(x / ratio_x - mx)
        map_y = int(y / ratio_y - my)
        return map_x, map_y

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                self.map_layer.zoom += .25
            elif event.key == pygame.K_MINUS:
                value = self.map_layer.zoom - .25
                if value > 0:
                    self.map_layer.zoom = value

            if event.key == pygame.K_UP:
                self.car.speed += 1
            elif event.key == pygame.K_DOWN:
                self.car.speed -= 1
            elif event.key == pygame.K_LEFT:
                self.car.angle_speed = -4
            elif event.key == pygame.K_RIGHT:
                self.car.angle_speed = 4
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.car.angle_speed = 0
            elif event.key == pygame.K_RIGHT:
                self.car.angle_speed = 0

    def handle_click(self):
        poll = pygame.event.poll
        event = poll()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            mouse_position_in_map = self.convert_screen_coordinate_2_map_coordinate(pos)
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

                # self.display_traffic_light()
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
                self.render_car(start_point)

        return 0

    @staticmethod
    def get_rect_with_point(point, bound=16):
        print(point)
        x, y = point
        max_x, max_y, min_x, min_y = x + bound, y + bound, x - bound, y - bound

        return Polygon([(max_x, max_y), (max_x, min_y), (min_x, min_y), (min_x, max_y)])


    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            dt = clock.tick(60)/1000
            if len(self.start_end) < 2:
                self.handle_click()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
                    self.handle_input(event)

            self.update(dt)
            self.draw(screen)

            if self.path_sides:
                pygame.draw.lines(
                    screen,
                    Color('purple'),
                    False,
                    self.map_layer.translate_points(self.path_sides['left_side_points']),
                    4
                )
                pygame.draw.lines(
                    screen,
                    Color('purple'),
                    False,
                    self.map_layer.translate_points(self.path_sides['right_side_points']),
                    4
                )

            if self.car.display == True:
                car_polygon = self.car.get_polygon()
                pygame.draw.lines(
                    screen,
                    Color('red'),
                    True,
                    self.map_layer.translate_points(car_polygon),
                    4
                )
            pygame.display.flip()

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = utils.init_screen(950, 950)
    pygame.display.set_caption('Self-Driving Car')
    
    try:
        game = Game()    
        game.init_group()
        game.run()
    except:
        pygame.quit()
        raise