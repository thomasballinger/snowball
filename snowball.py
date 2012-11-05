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

        global snowflakes
        global snowballs

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

            # Game Logic

            # Move snowflakes
            for snowflake in snowflakes:
                snowflake.move(0, -1)
                snowflake.wind_move(wind.xSpeed, wind.ySpeed)

            quadtree = Quadtree()
            for leaf in quadtree.analyze(snowflakes):
                for snowflake in leaf:
                    for other in leaf:
                        if snowflake.x == other.x and snowflake.y == other.y:
                            continue
                        elif collision(snowflake.x, snowflake.y, snowflake.r,
                                       other.x, other.y, other.r):
                                if snowflake.area >= other.area:
                                    snowflake.area += math.pi * snowflake.r**2
                                    snowflake.true_area += math.pi * snowflake.r**2
                                    snowflake.r = int(math.sqrt(snowflake.area/math.pi))
                                    other.x, other.y, other.r = reset()

                            

            # Collisions
#            for snowflake in snowflakes:
#                for other in snowflakes:
#                    if snowflake.x == other.x and snowflake.y == other.y:
#                        continue
#                    if collision(snowflake.x, snowflake.y, snowflake.r,
#                                 other.x, other.y, other.r):
#                        if snowflake.area >= other.area:
#                            snowflake.area += math.pi * snowflake.r**2
#                            snowflake.true_area += math.pi * snowflake.r**2
#                            snowflake.r = int(math.sqrt(snowflake.area/math.pi))
#
#                            x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
#                            y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
#                            r = random.randrange(1, 8)
#                            snowflake.x, snowflake.y, snowflake.r = x, y, r

            for snowball in snowballs:
                for snowflake in snowflakes:
                    if collision(snowball.x, snowball.y, snowball.r,
                                 snowflake.x, snowflake.y, snowflake.r):
                        if snowflake.area >= snowball.area:
                            self.event_manager.post(TickEvent(game_over=True))
                            return
                        else:
                            snowball.area += snowflake.area
                            snowball.true_area += snowflake.true_area
                            snowball.r = int(math.sqrt(snowball.area/math.pi))
                            snowflake.x, snowflake.y, snowflake.r = reset()

                for other in snowballs:
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

            for snowflake in snowflakes:
                if snowflake.y < SNOW_Y_MIN:
                    snowflake.x, snowflake.y, snowflake.r = reset()

            # Known bugs:
            # Not yet written for multiplayer, just laid foundation/frameworks
            # You lose screen
            # Snowball has to be "eliminated" upon game over, currently just not drawn










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

        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball: bad luck")

        self.font = pygame.font.Font(None, 100)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()




    def notify(self, event):

        global snowflakes
        global snowballs

        self.window.fill(black)
        
        if isinstance(event, TickEvent):

            for snowflake in snowflakes:
                snowflake.draw(self.window)            

            if event.game_over:
                text = self.font.render('You Lose', True, red)
                text_rectangle = text.get_rect()
                text_rectangle.centerx = self.window.get_rect().centerx
                text_rectangle.centery = self.window.get_rect().centery
                self.window.blit(text, text_rectangle)
            else:
                snowballs[0].draw(self.window, antialias=True)

            pygame.display.flip()

            self.clock.tick(frames)

        if isinstance(event, QuitEvent):
            pass


class Quadtree:
    def __init__(self):
        # Subregions start empty
        self.nw = self.ne = self.se = self.sw = None

    def analyze(self, snowObjects, maxLevels=8, bounds=None):

        maxLevels -= 1
        if maxLevels == 0:
            return([snowObjects])

        if bounds:
            top, right, bottom, left = bounds
        else:
            top = min(snowObject.top() for snowObject in snowObjects)
            right = max(snowObject.right() for snowObject in snowObjects)
            bottom = max(snowObject.bottom() for snowObject in snowObjects)
            left = min(snowObject.left() for snowObject in snowObjects)
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        self.objects = []
        nw_objects = []
        ne_objects = []
        se_objects = []
        sw_objects = []

        for obj in snowObjects:
            if obj.top <= center_y and obj.left <= center_x:
                nw_objects.append(obj)
            if obj.top <= center_y and obj.right >= center_x:
                ne_objects.append(obj)
            if obj.bottom >= center_y and obj.right >= center_x:
                se_objects.append(obj)
            if obj.bottom >= center_y and obj.left <= center_x:
                sw_objects.append(obj)

        if nw_objects:
            self.nw = self.analyze(nw_objects, maxLevels,
                               (top, center_x, center_y, left))
        if ne_objects:
            self.ne = self.analyze(ne_objects, maxLevels,
                               (top, right, center_y, center_x))
        if se_objects:
            self.se = self.analyze(se_objects, maxLevels,
                               (center_y, right, bottom, center_x))
        if sw_objects:
            self.sw = self.analyze(sw_objects, maxLevels,
                               (center_y, center_x, bottom, left))

        return(self.nw + self.ne + self.se + self.sw)






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

    def top(self):
        return(self.y - self.r) 
    
    def bottom(self):
        return(self.y + self.r)

    def left(self):
        return(self.x - self.r)

    def right(self):
        return(self.x + self.r)

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
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.r)

class Snowstorm:
    def __init__(self, numberOfSnowflakes, xMin, xMax, yMin, yMax):
        self.intensity = numberOfSnowflakes
        self.xMin, self.xMax = xMin, xMax
        self.yMin, self.yMax = yMin, yMax

    def attributes(self, typeOfSnow, playerRadius=None, 
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
            for i in range(self.intensity):
                x = (self.xMax * (i + 1)) / (self.intensity + 1)
                y = (self.yMax * (i + 1)) / (self.intensity + 1)
                r = playerRadius
                attrs.append(Snowflake(x, y, r, 1, playerColors[i]))
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

def reset():
    """Return a tuple of x, y, r values to reset a snowflake."""
    x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
    y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
    r = random.randrange(1, 8)
    return((x, y, r))

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
snowballs = balls.attributes('Snowballs', MINIMUM_SNOWBALL_RADIUS, [green])

# Snowflakes
flakes = Snowstorm(1000, SNOW_X_MIN, SNOW_X_MAX, SNOW_Y_MIN, SNOW_Y_MAX)
snowflakes = flakes.attributes('Snowflakes')

# Wind
wind = Wind(0,0)

# Frames of screen
frames = 30
pps = 1.0/frames # pixels per second

state = 'Start'
game = Game(state)

# Main function

def main():
    # Instantiate event_manager
    event_manager = EventManager()

    # Instantiate view and controllers, as well as registering them
    # as listeners in event_manager
    game_engine = GameEngineController(event_manager, snowballs, snowflakes,
                                       wind)
    view = View(event_manager, snowballs, snowflakes)
    state = StateController(event_manager) 

    state.run()

main()
