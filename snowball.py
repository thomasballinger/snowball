import math
import pickle
import pygame
import pygame.gfxdraw
import random
import socket
import sys
import weakref

# Server stuff

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MAX = 65535
PORT = 1060

#  Global Parameters  #

WIND_MAX = 10
X_WIND = [-2, 1, 1, 0, 0, 0, 0, 1, 1, 2]
Y_WIND = [-2, 1, 1, 0, 0, 0, 0, 1, 1, 2]
MINIMUM_SNOWBALL_RADIUS = 3
MAX_SNOWBALL_SPEED = 20

# Set the width and height of the screen [width,height]

X_MAX = 1200
X_MID = X_MAX // 2
Y_MAX = 500
SCREEN_SIZE =[X_MAX, Y_MAX]

# Set the area of the snowstorm

SNOW_X_MAX = X_MAX + 200
SNOW_X_MIN = -200
SNOW_Y_MAX = Y_MAX + 300
SNOW_Y_MIN = -300

# Dampening Factors
X_DAMPEN = 1000
Y_DAMPEN = 500

# Helper Functions

def sticky_sum(initial, shift):
    """Given an initial number and a shift to add to it, return the zero
    sticky sum."""
    if initial < 0:
        result = min(0, initial + shift)
        return(result)
    elif initial > 0:
        result = max(0, initial + shift)
        return(result)
    else: # initial == 0
        return(0)

def dampen(initial, dampenAmount):
    """ Given a initial number and a dampening amount, return the dampened
    result as an int."""
    initial_sign = math.copysign(initial, 1)
    dampenAmount = math.copysign(-initial_sign, dampenAmount)
    result = sticky_sum(initial, dampenAmount)
    return(int(result))

#  Classes  #

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


class TickEvent:
    def __init__(self, game_over=False):
        self.game_over = game_over


class QuitEvent:
    def __init__(self):
        pass


class GameEngineController:
    def __init__(self, eventManager, snowballs, snowflakes, wind):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.snowballs = snowballs
        self.snowflakes = snowflakes
        self.wind = wind

    def notify(self, event):

        quit = None

        if isinstance(event, TickEvent):

            # Quitting
            for game_event in pygame.event.get():
                if game_event.type == pygame.QUIT:
                    quit = QuitEvent()

            keys_pressed = pygame.key.get_pressed()

            if keys_pressed[pygame.ESCAPE]:
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
                snowball.move(0, -snowball.speed)

            if keys_pressed[pygame.K_DOWN]:
                snowball.move(0, snowball.speed)

            if keys_pressed[pygame.K_LEFT]:
                snowball.move(-snowball.speed, 0)

            if keys_pressed[pygame.K_RIGHT]:
                snowball.move(snowball.speed, 0)

            if keys_pressed[pygame.K_SPACE]:
                snowball.compress(snowball.area/100)
                print('snowball area: %d' % snowball.area)
                print('snowball true area: %d' % snowball.true_area)
                print('snowball radius: %d' % snowball.r)

            # Game Logic

            # Move snowflakes
            for snowflake in self.snowflakes:
                snowflake.move(0, -1)
                snowflake.wind_move(wind.xSpeed, wind.ySpeed)

            # Collisions
            for snowflake in self.snowflakes:
                for other in self.snowflakes:
                    if snowflake.x == other.x and snowflake.y == other.y:
                        continue
                    if collision(snowflake.x, snowflake.y, snowflake.r,
                                 other.x, other.y, other.r):
                        if snowflake.area >= other.area:
                            snowflake.area += math.pi * snowflake.r**2
                            snowflake.true_area += math.pi * snowflake.r**2
                            snowflake.r = int(math.sqrt(snowflake.area/math.pi))

                            x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
                            y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
                            r = random.randrange(1, 8)
                            snowflake.x, snowflake.y, snowflake.r = x, y, r

            for snowball in self.snowballs:
                if collision(snowball.x, snowball.y, snowball.r,
                             snowflake.x, snowflake.y, snowflake.r):
                    if snowflake.area >= snowball.area:
                        self.event_manager.post(TickEvent(game_over=True))
                        return
                    else:
                        snowball.area += snowflake.area
                        snowball.true_area += snowflake.true_area
                        snowball.r = int(math.sqrt(snowball.area/math.pi))

                for other in self.snowballs:
                    if snowball.x == other.x and snowball.y == other.y:
                        continue
                    if collision(snowball.x, snowball.y, snowball.r,
                                 other.x, other.y, other.r):
                        if other.area >= snowball.area:
                            self.event_manager.post(TickEvent(game_over=True))
                            return
                        else:
                            snowball.area += other.area
                            snowball.true_area += other.true_area
                            snowball.r = int(math.sqrt(snowball.area/math.pi))






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

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.keep_going = False

class View:
    def __init__(self):

        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball: bad luck")

        self.font = pygame.font.Font(None, 100)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()




    def notify(self, event):
        if isinstance(event, TickEvent):

            for (index, snowflake) in enumerate(snowflake_positions):
                snowflake.draw(self.window)            

            if event.game_over:
                text = self.font.render('You Lose', True, red)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = self.window.get_rect().centery
                self.window.blit(text, text_rectangle)
            else:
                snowball.draw(self.window, antialias=True)

            pygame.display.flip()

            self.clock.tick(frames)

        if isinstance(event, QuitEvent):
            pass


class Game:
    def __init__(self, state):
        self.state = state

    def change_to(self, state):
        if state == 'You Lose':
            pass
        elif state == 'You Win':
            pass


class Snowflake:
    def __init__(self, xPosition, yPosition, radius, speed, color):
        self.x = xPosition
        self.y = yPosition
        self.r = radius
        self.speed = speed
        self.color = color
        self.area = math.pi * self.r**2
        self.true_area = self.area # Area if never compressed

    def __str__(self):
        return('(%d, %d)' % (self.x, self.y))

    def position(self):
        return([self.xPosition, self.yPosition])

    def move(self, x, y):
        """Move x and y position of Snowflake."""
        self.x += x
        self.y += y

    def wind_move(self, xSpeed, ySpeed):
        """Movement to Snowflake caused by wind."""
        self.x += dampen(xSpeed, self.true_area / X_DAMPEN)
        self.y += dampen(ySpeed, self.true_area / Y_DAMPEN)

    def distance_from(self, position):
        """Distance from Snowflake to another [x, y] position"""
        distance = math.sqrt((self.x - position[0])**2
                             + (self.y - position[1])**2)
        return(distance)

    def resize(self, amount):
        """Given amount to change radius, return radius sticky at 1."""
        if (self.r + amount) > 1:
            self.r + amount
        else:
            self.r == 1 # Cannot resize to nothing

    def recolor(self, newColor):
        # Make super colors later maybe
        # maybe the snow will be RGB and add to each RGB value!
        self.color = newColor

    def change_speed(self, amount):
        if (self.speed + amount) > 0:
            self.speed += amount
        else:
            self.speed = 1

    def compress(self, amount):
        """Given an amount to compress Snowflake, return compressed area."""
        minimum_area = MINIMUM_SNOWBALL_RADIUS**2 * math.pi
        result = max(minimum_area, self.area - amount)
        resulting_radius = math.sqrt(result/math.pi)
        self.r = int(resulting_radius)
        self.area = int(result)

    def draw(self, screen, antialias=False):
        """Draw snowflake on screen."""
        if antialias:
            pygame.gfxdraw.aacircle(screen, self.x, self.y, self.r, self.color)
        pygame.draw.cirlce(screen, self.color, [self.x, self.y], self.r)

class Snowstorm:
    def __init__(self, numberOfSnowflakes, xMin, xMax, yMin, yMax):
        self.intensity = numberOfSnowflakes
        self.xMin, self.xMax = xMin, xMax
        self.yMin, self.yMax = yMin, yMax

    def attributes(self, typeOfSnow, playerCount=None, playerRadius=None, 
                  playerColors=None):
        """Return list of Snowflakes with given attributes."""
        attrs = []

        if typeOfSnow == 'Snowflakes':
            for i in range(self.intensity):
                x = random.randrange(self.xMin, self.xMax)
                y = random.randrange(self.yMin, self.yMax)
                r = random.randrange(1, 10)
                attrs.append(Snowflake(x, y, r, 1, white))
            return(attrs)

        if typeOfSnow == 'Snowballs':
            player = 0
            for i in range(self.intensity):
                x = self.xMax / playerCount
                y = self.yMax / playerCount
                r = playerRadius
                attrs.append(Snowflake(x, y, r, 1, playerColors[player]))
                player += 1
            return(attrs)


class Wind:
    def __init__(self, xSpeed, ySpeed):
        self.xSpeed, self.ySpeed = xSpeed, ySpeed

    def change_speed(self, xChange, yChange):
        self.xSpeed += xChange
        self.ySpeed += yChange
        if math.fabs(self.xSpeed) >= WIND_MAX:
            if math.fabs(self.ySpeed) >= WIND_MAX:
                self.ySpeed = math.copysign(WIND_MAX, self.ySpeed)
            self.xSpeed = math.copysign(WIND_MAX, self.xSpeed)

    def x_change(self, transition):
        "Uniformly draw the wind speed change in the x axis"
        i = random.randrange(len(transition))
        return(transition[i])

    def y_change(self, transition):
        "Uniformly draw the wind speed change in the y axis"
        i = random.randrange(len(transition))
        return(transition[i])

    #def effect_on(self, obj):
    #    return(wind.speed dampens by obj.r // 5?

#  Functions  #

def collision(xOne, yOne, rOne, xTwo, yTwo, rTwo):
    """Given size and space parameters for each object, return boolean for
       whether collision occurs"""
    origin_distance = math.sqrt((xOne - xTwo)**2 + (yOne - yTwo)**2)
    collision_distance = rOne + rTwo
    if origin_distance <= collision_distance:
        return(True)
    else:
        return(False)


# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 255)

#Loop until the user clicks the close button.
done=False

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# Snowballs
balls = Snowstorm(1, 0, X_MAX, 0, Y_MAX)
snowballs = balls.attributes()

# Snowflakes
flakes = Snowstorm(1000, SNOW_X_MIN, SNOW_X_MAX, SNOW_Y_MIN, SNOW_Y_MAX)
snowflakes = flakes.attributes()

# Wind
wind = Wind(0,0)

# Frames of screen
frames = 30
pps = 1.0/frames # pixels per second

# Instantiate font
font = pygame.font.Font(None, 100)

state = 'Start'
game = Game(state)

# Main function

def main():
    # Instantiate event_manager
    event_manager = EventManager()

    # Instantiate view and controllers, as well as registering them
    # as listeners in event_manager
    game_engine = GameEngineController(event_manager)
    view = View(event_manager)
    state = StateController(event_manager) 

    state.run()
