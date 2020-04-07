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

        self.hold_k_left = False
        self.hold_k_right = False
        self.hold_k_forward = False
        self.hold_k_backward = False

    def init_group(self):
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=True)
        self.map_layer.zoom = 0.3
        self.zoomchange = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

    def init_world(self):
        self.car.set_position(450, 450, 90)
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
        print('handle')
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                self.map_layer.zoom += .25
            elif event.key == pygame.K_MINUS:
                value = self.map_layer.zoom - .25
                if value > 0:
                    self.map_layer.zoom = value
            elif event.key == pygame.K_SPACE:
                self.car.velocity += 5

            if event.key == pygame.K_LEFT:
                self.hold_k_left = True
            elif event.key == pygame.K_RIGHT:
                self.hold_k_right = True

            if event.key == pygame.K_UP:
                self.hold_k_forward = True
            elif event.key == pygame.K_DOWN:
                self.hold_k_backward = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                self.hold_k_left = False
                self.hold_k_right = False
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.hold_k_forward = False
                self.hold_k_backward = False


    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            dt = clock.tick(60)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                self.handle_input(event)

            if self.hold_k_left:
                self.car.angle += 2.5
            if self.hold_k_right:
                self.car.angle -= 2.5
            if self.hold_k_forward:
                self.car.move_forward()
            if self.hold_k_backward:
                self.car.move_backward()

            # screen.fill((95, 183, 229)) # sky color
            w, h = pygame.display.get_surface().get_size()
            text = self.font.render("Hello World !", 1, (255, 0, 0))
            text_rect = text.get_rect()
            text_rect.right = w / 2 + text_rect.w / 2
            text_rect.top = h / 2 - text_rect.h / 2
            screen.blit(text, text_rect)

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