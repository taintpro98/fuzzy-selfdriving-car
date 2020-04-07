import pygame, sys
from pygame.locals import *
from pytmx.util_pygame import load_pygame
from map import Map
import pyscroll
from pyscroll.group import PyscrollGroup
import utils
from car import Car

class Game:
    def __init__(self):
        self.running = False
        self.file_name = 'map/map.tmx'
        self.tmx_data = load_pygame(self.file_name)
        self.map = Map(tmx_data=self.tmx_data)
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.car = Car('mymap/car.png')
        self.focus_car = False

    def init_group(self):
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=True)
        self.map_layer.zoom = 0.3
        self.zoomchange = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

    def init_world(self):
        self.car.set_position((450, 450), 0)
        self.render_car()

    def update(self, dt):
        self.group.update(dt)

    def draw(self, surface):
        if self.focus_car:
            self.group.center(self.car.rect.center)
        self.group.draw(surface)

    def render_car(self):
        self.focus_car = True
        self.group.add(self.car)

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


    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            dt = clock.tick(60)/1000
            print(dt)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                self.handle_input(event)

            self.update(dt)
            self.draw(screen)

            pygame.display.flip()

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = utils.init_screen(950, 950)
    pygame.display.set_caption('Self-Driving Car')
    
    try:
        game = Game()    
        game.init_group()
        game.init_world()
        game.run()
    except:
        pygame.quit()
        raise