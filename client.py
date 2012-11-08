# This is the client side
import json
import math
import pdb
import pygame
import pygame.gfxdraw
import socket
import time
import weakref

#import server

# socket family is AF_INET, the Internet family of protocols
# SOCK_DGRAM refers to using UDP (and sending 'datagrams' aka packets)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


MAX = 65535
PORT = 1060
SERVER = '127.0.0.1'
TICK_TIME = 30
lt = int(round(time.time() * 1000))

# Server will delegate game_master identity to first client to connect.
# If True, this client will initialize the start of the game
game_master = False
players = 0

SCREEN_SIZE = [1200, 500]

class Event:
    """Superclass for any event that needs to be sent to the EventManager."""
    def __init__(self):
        self.name = "Event"


class EventManager:
    """Coordinates communication between Model, View, and Controller."""
    def __init__(self):
        self.listeners = weakref.WeakKeyDictionary()

    # Listeners are objects that are awaiting input on which event they should
    # process (ie TickEvent or QuitEvent)
    def register_listener(self, listener):
        self.listeners[listener] = 1

    def unregister_listener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        """Post a new event broadcasted to listeners"""
        for listener in self.listeners.keys():
            # NOTE: if listener was unregistered then it will be gone already
            listener.notify(event)


class ConnectEvent:
    def __init__(self):
        pass


class StartEvent:
    def __init__(self):
        pass


class TickEvent:
    def __init__(self, game_over=False):
        self.game_over = game_over


class QuitEvent:
    def __init__(self):
        pass


class StateController:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.connect = True
        self.start = True
        self.keep_going = True

    def run(self):

        global lt
        global players
        global game_master

        while self.connect and self.start and self.keep_going:
            event = ConnectEvent()
            self.event_manager.post(event)
            t = int(round(time.time() * 1000))
            if TICK_TIME - t + lt > 0:
                s.timeout(TICK_TIME - t + lt)
                try:
                    players, _ = s.recvfrom(MAX)
                except socket.timeout:
                    print "server didn't respond"
                    clock.tick(32)
                    lt = t
                    continue
            if len(players) > 2:
                instruction, players = json.loads(players)
                if instruction == 'MASTER':
                    game_master = True
            players = int(players)
            clock.tick(32)
            lt = t
            event = StartEvent()
            self.notify(event)

        while self.start and self.keep_going:
            event = StartEvent()
            self.event_manager.post(event)
            t = int(round(time.time() * 1000))
            if TICK_TIME - t + lt > 0:
                s.timeout(TICK_TIME - t + lt)
                try:
                    players, _ = s.recvfrom(MAX)
                except socket.timeout:
                    print "server didn't respond"
                    clock.tick(32)
                    lt = t
                    continue
            if len(players) > 2:
                instruction, players = json.loads(players)
            players = int(players)
            clock.tick(32)
            lt = t
            if instruction == 'START':
                event = TickEvent()
                self.notify(event)

        while self.keep_going:
            event = TickEvent()
            self.event_manager.post(event)
            clock.tick(32)

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.keep_going = False
        if isinstance(event, TickEvent):
            self.start = False
        if isinstance(event, StartEvent):
            self.connect = False


class KeyboardController:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)

    def notify(self, event):

        quit = None

        if isinstance(event, ConnectEvent):

            # Quitting
            for game_event in pygame.event.get():
                if game_event.type == pygame.QUIT:
                    quit = QuitEvent()

            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                quit = QuitEvent()

            if quit:
                self.event_manager.post(quit)
                return

            if pressed[pygame.K_SPACE]:
                keys_pressed = json.dumps(['SPACE'], separators=(',',':'))
                s.sendto(keys_pressed, (SERVER, PORT))

        if isinstance(event, StartEvent):

            # Quitting
            for game_event in pygame.event.get():
                if game_event.type == pygame.QUIT:
                    quit = QuitEvent()

            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                quit = QuitEvent()

            if quit:
                self.event_manager.post(quit)
                return

            if pressed[pygame.K_s]:
                start = json.dumps(['START'], separators=(',',':'))
                s.sendto(start, (SERVER, PORT))


        if isinstance(event, TickEvent) or isinstance(event, StartEvent):

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

            if isinstance(event,TickEvent):
                keys_pressed = json.dumps(keys_pressed, separators=(',',':'))
                s.sendto(keys_pressed, (SERVER, PORT))
            elif 'SPACE' in keys_pressed:
                keys_pressed = json.dumps(keys_pressed, separators=(',',':'))
                s.sendto(keys_pressed, (SERVER, PORT))



class View:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)

        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball, the game")

        self.title = pygame.font.Font(None, 100)
        self.msg = pygame.font.Font(None, 40)


    def notify(self, event):

        self.window.fill(black)


        if isinstance(event, ConnectEvent):

            title = self.title.render('~*~snowball~*~', True, white)
            title_rectangle = title.get_rect()
            title_rectangle.centerx = self.window.get_rect().centerx
            title_rectangle.centery = 200
            self.window.blit(title, title_rectangle)

            text = self.msg.render('hit SPACE to connect to server', True, blue)
            text_rectangle = text.get_rect()
            text_rectangle.centerx = self.window.get_rect().centerx
            text_rectangle.centery = 400
            self.window.blit(text, text_rectangle)

            pygame.display.flip()

        if isinstance(event, StartEvent):

            title = self.title.render('~*~snowball~*~', True, white)
            title_rectangle = title.get_rect()
            title_rectangle.centerx = self.window.get_rect().centerx
            title_rectangle.centery = 200
            self.window.blit(title, title_rectangle)

            if game_master:
                text = self.msg.render('snowballs formed: %d' % players, True, blue)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = 400
                self.window.blit(text, text_rectangle)
            else:
                text = self.msg.render('snowballs formed: %d' % players, True, white)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = 350
                self.window.blit(text, text_rectangle)

                text2 = self.msg.render('hit SPACE to start game', True, blue)
                text2_rectangle = text2.get_rect()
                text2_rectangle.centerx = self.window.get_rect().centerx
                text2_rectangle.centery = 400
                self.window.blit(text2, text2_rectangle)

            pygame.display.flip()

        if isinstance(event, TickEvent):

            snowstorm, address = s.recvfrom(MAX)
            snowstorm = json.loads(snowstorm)

            if len(snowstorm):
                for snow in snowstorm:
                    x, y, r, c = snow
                    pygame.gfxdraw.aacircle(self.window, x, y, r, c)
                    pygame.gfxdraw.filled_circle(self.window, x, y, r, c)

            if event.game_over:
                text = self.font.render('You Lose', True, red)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = self.window.get_rect().centery
                self.window.blit(text, text_rectangle)

            pygame.display.flip()


        if isinstance(event, QuitEvent):
            pass


# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 255)


pygame.init()

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

def main():
    event_manager = EventManager()
    keyboard = KeyboardController(event_manager)
    state = StateController(event_manager)
    view = View(event_manager)

    state.run()

main()

