# This is the client side
import math
import pdb
import pygame
import pygame.gfxdraw
import socket

snowstorm = 'list of objects'

class Event:
    """Superclass for any event that needs to be sent to the EventManager."""
    def __init__(self):
        self.name = "Event"


class TickEvent:
    def __init__(self, game_over=False):
        self.game_over = game_over


class QuitEvent:
    def __init__(self):
        pass


class KeyboardController:
    def __init__(self, eventManager, snowballs, snowflakes, wind):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.snowballs = snowballs
        self.snowflakes = snowflakes
        self.wind = wind

    def notify(self, event):

        quit = None

        player = self.snowballs[0]

        if isinstance(event, TickEvent):

            # Quitting
            for game_event in pygame.event.get():
                if game_event.type == pygame.QUIT:
                    quit = QuitEvent()

            keys_pressed = pygame.key.get_pressed()

            if keys_pressed[pygame.K_ESCAPE]:
                quit = QuitEvent()

            if quit:
                self.event_manager.post(quit)
                return

            # Keyboard Admin Controls
            if keys_pressed[pygame.K_u]:
                frames += 1
                print('frames: %d' % frames)

            if keys_pressed[pygame.K_d]:
                frames -= 1
                print('frames: %d' % frames)

            # Keyboard Game Controls
            if keys_pressed[pygame.K_UP]:
                player.move(0, -player.speed)

            if keys_pressed[pygame.K_DOWN]:
                player.move(0, player.speed)

            if keys_pressed[pygame.K_LEFT]:
                player.move(-player.speed, 0)

            if keys_pressed[pygame.K_RIGHT]:
                player.move(player.speed, 0)

            if keys_pressed[pygame.K_SPACE]:
                player.compress(player.area/100)
                print('snowball area: %d' % player.area)
                print('snowball true area: %d' % player.true_area)
                print('snowball radius: %d' % player.r)


class StateController:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.keep_going = True

    def run(self):
        while self.keep_going:
            # TickEvent starts events for the general game
            event = TickEvent()
            self.event_manager.post(event)
            print('frame')

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.keep_going = False

class View:
    def __init__(self, eventManager, snowflakes, snowballs):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.snowflakes = snowflakes
        self.snowballs = snowballs

        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball: bad luck")

        self.font = pygame.font.Font(None, 100)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

    def notify(self, event):

        self.window.fill(black)
        
        if isinstance(event, TickEvent):

            for snowflake in self.snowflakes:
                snowflake.draw(self.window, antialias=True)            

            if event.game_over:
                text = self.font.render('You Lose', True, red)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = self.window.get_rect().centery
                self.window.blit(text, text_rectangle)
            else:
                self.snowballs[0].draw(self.window, antialias=True)

            pygame.display.flip()

            self.clock.tick(frames)

        if isinstance(event, QuitEvent):
            pass


