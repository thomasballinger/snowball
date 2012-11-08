# This is the client side
import json
import math
import pdb
import pygame
import pygame.gfxdraw
import socket
import weakref

#import server

# socket family is AF_INET, the Internet family of protocols
# SOCK_DGRAM refers to using UDP (and sending 'datagrams' aka packets)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


MAX = 65535
PORT = 1060
SERVER = '127.0.0.1'
TICK_TIME = 31

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

        while self.connect and self.start and self.keep_going:
            event = ConnectEvent()
            self.event_manager.post(event)

        while self.start and self.keep_going:
            print 'connecting to server...'
            msg = 'h', 'i' * random.randint(2, 20)
            s.sendto(msg, (SERVER, PORT))
            s.settimeout(2)
            try:
                server_msg, addr = s.recvfrom(MAX)
            except socket.timeout:
                print """Can't seem to connect to the server...
                         1. Is it on?
                         2. Do you have the correct IP address for the server?
                         (Or you could just try again?)"""
                return
            if int(server_msg) == (len(msg) - 1):
                event = StartEvent()
                self.event_manager.post(event)
            else:
                del server_msg
                print """You have the wrong IP address for the server."""

        while self.keep_going:
            event = TickEvent()
            self.event_manager.post(event)

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

            self.clock.tick(32)

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

            self.clock.tick(32)

        if isinstance(event, QuitEvent):
            pass


# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 255)



def main():
    event_manager = EventManager()
    keyboard = KeyboardController(event_manager)
    state = StateController(event_manager)
    view = View(event_manager)

    state.run()

main()

