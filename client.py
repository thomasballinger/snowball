# This is the client side
import json
import math
import pdb
import pygame
import pygame.gfxdraw
import socket

#import server

# socket family is AF_INET, the Internet family of protocols
# SOCK_DGRAM refers to using UDP (and sending 'datagrams' aka packets)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


MAX = 65535
PORT = 1060


SCREEN_SIZE = [1200, 500]

class Event:
    """Superclass for any event that needs to be sent to the EventManager."""
    def __init__(self):
        self.name = "Event"


class StartEvent:
    def __init__(self):
        pass


class TickEvent:
    def __init__(self, game_over=False):
        self.game_over = game_over


class QuitEvent:
    def __init__(self):
        pass


class KeyboardController:
    def __init__(self):
        pass
#        self.event_manager = eventManager
#        self.event_manager.register_listener(self)

    def notify(self, event):

        quit = None

        if isinstance(event, TickEvent):

            # Quitting
            for game_event in pygame.event.get():
                if game_event.type == pygame.QUIT:
                    quit = QuitEvent()

            pressed = pygame.key.get_pressed()
            keys_pressed = []

            if pressed[pygame.K_ESCAPE]:
                quit = QuitEvent()

            if quit:
                self.event_manager.post(quit)
                return

            # Keyboard Admin Controls
            if pressed[pygame.K_u]:
                keys_pressed += ['u']

            if pressed[pygame.K_d]:
                keys_pressed += ['d']

            # Keyboard Game Controls
            if pressed[pygame.K_UP]:
                keys_pressed += ['UP']

            if pressed[pygame.K_DOWN]:
                keys_pressed += ['DOWN']

            if pressed[pygame.K_LEFT]:
                keys_pressed += ['LEFT']

            if pressed[pygame.K_RIGHT]:
                keys_pressed += ['RIGHT']

            if pressed[pygame.K_SPACE]:
                keys_pressed += ['SPACE']

            keys_pressed = json.dumps(keys_pressed)
            s.sendto(keys_pressed, ('127.0.0.1', PORT))



class View:
    def __init__(self):
        #self.event_manager = eventManager
        #self.event_manager.register_listener(self)

        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball: bad luck")

        self.font = pygame.font.Font(None, 100)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

    def notify(self, event):

        self.window.fill(black)

        if isinstance(event, StartEvent):
            text = self.font.render('~*~snowball~*~', True, white)
            text_rectangle = text.get_rect()
            text_rectangle.centerx = self.window.get_rect().centerx
            text_rectangle.centery = self.window.get_rect().centery
            self.window.blit(text, text_rectangle)

            pygame.display.flip()

            self.clock.tick(30)

        if isinstance(event, TickEvent):

            snowstorm, address = s.recvfrom(MAX)
            snowstorm = json.loads(snowstorm)

            if len(snowstorm):
                for snow in snowstorm:
                    x, y, r, c = snow
                    pygame.gfxdraw.aacircle(self.window, x, y, r, c)

            if event.game_over:
                text = self.font.render('You Lose', True, red)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = self.window.get_rect().centery
                self.window.blit(text, text_rectangle)

            pygame.display.flip()

            self.clock.tick(30)

        if isinstance(event, QuitEvent):
            pass


class TestView:
    def __init__(self):
        self.snowstorm = None

        pygame.init()
        self.window = pygame.display.set_mode([50,50])
        pygame.display.set_caption("snowball: bad luck")

        self.font = pygame.font.Font(None, 100)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

    def notify(self, event):

        self.window.fill(black)

        if isinstance(event, TickEvent):

            pygame.display.flip()

            self.clock.tick(30)

# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 255)



def main():
    keyboard = KeyboardController()
    view = View()
    while True:
        keyboard.notify(TickEvent())
        view.notify(TickEvent())

main()

