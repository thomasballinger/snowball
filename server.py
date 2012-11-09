# This is the server side
import json
import math
import pdb
import random
import socket
import sys
import threading
import time
import weakref

# socket family is AF_INET, the Internet family of protocols
# SOCK_DGRAM refers to using UDP (and sending 'datagrams' aka packets)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MAX = 65535
PORT = 1060

#  Global Parameters  #

TICK_TIME = 31

WIND_ON = False
WIND_MAX = 5
X_WIND = [-2]*2 + [-1]*20 + [0]*300 + [1]*20 + [2]*2
Y_WIND = [-2, 1, 1, 0, 0, 0, 0, 1, 1, 2]
MIN_SNOWBALL_R = 3
MAX_SNOWBALL_SPEED = 20
IMMUNE_TIME = 2000

# Set the width and height of the screen [width,height]

X_MAX = 1200
X_MID = X_MAX // 2
Y_MAX = 500

# Set the area of the snowstorm

SNOW_X_MAX = X_MAX + 500
SNOW_X_MIN = -500
SNOW_Y_MAX = Y_MAX + 300
SNOW_Y_MIN = -300

# Dampening Factors
X_DAMPEN = 100
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
    initial_sign = math.copysign(1, initial)
    dampenAmount = math.copysign(dampenAmount, -initial_sign)
    result = sticky_sum(initial, dampenAmount)
    return(int(result))

def current_time():
    return(int(round(time.time() * 100)))

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


class ConnectEvent:
    def __init__(self):
        pass


class TickEvent:
    def __init__(self, game_over=False):
        self.game_over = game_over


class QuitEvent:
    def __init__(self):
        pass


class Model:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, TickEvent):
            # Move snowflakes
            for snowflake in snowflakes:
                snowflake.move(0, -1)
                snowflake.wind_move(wind.xSpeed, wind.ySpeed)

            # Move snowballs
            for snowball in snowballs:
                snowball.wind_move(wind.xSpeed, wind.ySpeed)
                for client in clients.values():
                    if client[1] == snowball.c:
                        snowball.control(client[0])

            wind.change_speed(random.choice(X_WIND), 0)

            quadtree = Quadtree(snowflakes)
            for region in quadtree.regions():
                if len(region) == 1:
                    continue
                for snowflake in region:
                    for other in region:
                        if snowflake.x == other.x and snowflake.y == other.y:
                            continue
                        elif collision(snowflake.x, snowflake.y, snowflake.r,
                                       other.x, other.y, other.r):
                                if snowflake.area >= other.area and snowflake.area < 3000: 
                                    snowflake.area += other.area
                                    snowflake.true_area += other.true_area
                                    snowflake.r = int(math.sqrt(snowflake.area/math.pi))
                                    other.x, other.y, other.r, other.area, other.true_area = reset()

            for snowball in snowballs:
                for snowflake in snowflakes:
                    if collision(snowball.x, snowball.y, snowball.r,
                                 snowflake.x, snowflake.y, snowflake.r):
                        if snowflake.area >= snowball.area:
                            print 'ouch'
                            self.event_manager.post(TickEvent(game_over=True))
                            return
                        else:
                            print 'nom'
                            snowball.area += snowflake.area
                            snowball.true_area += snowflake.true_area
                            snowball.r = int(math.sqrt(snowball.area/math.pi))
                            snowflake.x, snowflake.y, snowflake.r, snowflake.area, snowflake.true_area = reset()

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

            for sf in snowflakes:
                if sf.y < SNOW_Y_MIN or sf.x < SNOW_X_MIN or sf.x > SNOW_X_MAX:
                    sf.x, sf.y, sf.r, sf.area, sf.true_area = reset()

            # TODO: Known bugs:
            # Not yet written for multiplayer, just laid foundation/frameworks
            # You lose screen
            # Snowball has to be "eliminated" upon game over, currently just not drawn


class PrintView:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)

    def notify(self, event):
        
        if isinstance(event, StartEvent):
            for addr in address:
                for ID in clientID:
                    s.sendto(ID, addr)
            pass

        if isinstance(event, TickEvent):
            snowstorm = snowflakes + snowballs
            snowstorm = json.dumps(serialize(snowstorm), separators=(',',':'))
            for addr in address:
                s.sendto(snowstorm, addr)

            if event.game_over:
                print 'Game Over'

        if isinstance(event, QuitEvent):
            print 'Quit Event'

lt = int(round(time.time() * 1000)) 
addresses = []
keys_pressed = []
IDs = [random.randrange(100000, 999999) for i in range(100)]
IDs = set(IDs)
clientID = {}
clients = {}
class StateController:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)
        self.master = None
        self.connect = True
        self.keep_going = True

    def run(self):

        s.bind(('127.0.0.1', PORT))
        print 'Listening at', s.getsockname()
        global address
        global keys_pressed
        global clients
        global IDs
        global clientID
        global lt

        player_cols = [green, blue, red, white, green, blue, red]

        while self.connect and self.keep_going:
            msg, addr = s.recvfrom(MAX)
            msg = json.loads(msg)
            if not self.master:
                if msg[0] == 'SPACE':
                    clients[addr] = [[], player_cols[0]]
                    #ID = random.choice(IDs)
                    #clientID[addr] = ID
                    #IDs.remove(ID)
                    msg = ['MASTER', 1]
                    s.sendto(msg, (addr, PORT))
                    self.master = addr
                    continue
            if addr == self.master:
                if msg[0] == 'START':
                    event = TickEvent()
                    self.notify(event)
                    continue
            if addr not in address:
                clients[addr] = [[], player_cols[len(clients.keys())]]
                #ID = random.choice(IDs)
                #clientID[addr] = ID
                #IDs.remove(ID)
            msg = len(clients.keys())
            s.sendto(msg, (addr, PORT))

        players = len(clients.keys())

        # Snowballs
        balls = Snowstorm(players, 0, X_MAX, 0, Y_MAX)
        snowballs = balls.attributes('Snowballs', MIN_SNOWBALL_R, player_cols[:players])

        # Snowflakes
        flakes = Snowstorm(700, SNOW_X_MIN, SNOW_X_MAX, SNOW_Y_MIN, SNOW_Y_MAX)
        snowflakes = flakes.attributes('Snowflakes')


        while self.keep_going:
            #count = 0.00
            #while count < 1.0/30:
            #    keys_pressed, addr = s.recvfrom(MAX)
            #    keys_pressed = json.loads(keys_pressed)
            #    address += [addr]
            #    del addr
            #    time.sleep(0.03)
            #print addr
            #print keys_pressed
            # TickEvent starts events for the general game
            event = TickEvent()
            self.event_manager.post(event)
            t = current_time()
            for client in clients.keys():
                clients[client] = [[], clients[client][1]]
            while TICK_TIME - t + lt > 0:
                s.timeout(TICK_TIME - t + lt)
                try:
                    keys_pressed, addr = s.recvfrom(MAX)
                except socket.timeout:
                    continue
                keys_pressed = json.loads(keys_pressed)
                if client in clients.keys():
                    clients[client] = [keys_pressed, clients[client][1]]
                t = current_time()
                    
    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.keep_going = False
        elif isinstance(event, TickEvent):
            self.connect = False


class ConnectionController:
    def __init__(self, eventManager):
        self.event_manager = eventManager
        self.event_manager.register_listener(self)

    def client_connect(self, client):
        event = ClientConnectEvent(client)
        self.event_manager.post(event)

    def notify(self):
        pass


class Quadtree:
    def __init__(self, snowObjects, maxLevels=6, bounds=None):
        # Subregions start empty
        self.nw = self.ne = self.se = self.sw = None

        maxLevels -= 1
        if maxLevels == 0:
            self.objects = [snowObjects]
            return

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
            if obj.top() <= center_y and obj.left() <= center_x:
                nw_objects.append(obj)
            if obj.top() <= center_y and obj.right() >= center_x:
                ne_objects.append(obj)
            if obj.bottom() >= center_y and obj.right() >= center_x:
                se_objects.append(obj)
            if obj.bottom() >= center_y and obj.left() <= center_x:
                sw_objects.append(obj)

        if nw_objects:
            self.nw = Quadtree(nw_objects, maxLevels,
                               (top, center_x, center_y, left))

        if ne_objects:
            self.ne = Quadtree(ne_objects, maxLevels,
                               (top, right, center_y, center_x))

        if se_objects:
            self.se = Quadtree(se_objects, maxLevels,
                               (center_y, right, bottom, center_x))

        if sw_objects:
            self.sw = Quadtree(sw_objects, maxLevels,
                               (center_y, center_x, bottom, left))

    def regions(self):
        region = []

        if self.nw == self.ne == self.se == self.sw:
            region = self.objects
        
        if self.nw:
            region += self.nw.regions()
        if self.ne:
            region += self.ne.regions()
        if self.se:
            region += self.se.regions()
        if self.sw:
            region += self.sw.regions()

        return(region)


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
        if WIND_ON:
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
        minimum_area = MIN_SNOWBALL_R**2 * math.pi
        result = max(minimum_area, self.area - amount)
        resulting_radius = math.sqrt(result/math.pi)
        self.r = int(resulting_radius)
        self.area = int(result)

    def draw(self, screen, antialias=False):
        """Draw snowflake on screen."""
        if antialias:
            pygame.gfxdraw.aacircle(screen, self.x, self.y, self.r, self.color)
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.r)

    def control(self, keysPressed):
        """Given a list of keysPressed, alter Snowflake's attributes."""

        if 'SPACE' in keysPressed:
            self.compress(self.area/100)
            limit = min(MAX_SNOWBALL_SPEED, int(self.true_area // (2 * self.area)))
            self.speed = max(1, limit)

        if 'UP' in keysPressed:
            self.move(0, -self.speed)

        if 'DOWN' in keysPressed:
            self.move(0, self.speed)

        if 'LEFT' in keysPressed:
            self.move(-self.speed, 0)

        if 'RIGHT' in keysPressed:
            self.move(self.speed, 0)
        

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
        if self.xSpeed >= WIND_MAX:
            self.xSpeed = WIND_MAX
        if self.xSpeed <= -WIND_MAX:
            self.xSpeed = -WIND_MAX
        if self.ySpeed >= WIND_MAX:
            self.ySpeed = WIND_MAX
        if self.ySpeed <= -WIND_MAX:
            self.ySpeed = -WIND_MAX

    def x_change(self, transition):
        "Uniformly draw the wind speed change in the x axis"
        i = random.randrange(len(transition))
        return(transition[i])

    def y_change(self, transition):
        "Uniformly draw the wind speed change in the y axis"
        i = random.randrange(len(transition))
        return(transition[i])

    def effect_on(self, obj):
        return(dampen(wind.speed, obj.r // 5))

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
    y = random.randrange(SNOW_Y_MAX, SNOW_Y_MAX + 200)
    r = random.randrange(1, 8)
    area = math.pi * r**2
    return((x, y, r, area, area))

def serialize(snowstorm):
    out = []
    for snow in snowstorm:
        x = snow.x
        y = snow.y
        r = snow.r
        c = snow.color
        out.append([x, y, r, c])
    return(out)


# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 255)

# Wind
wind = Wind(-1,0)

# Main function
def main():
    # Instantiate event_manager
    event_manager = EventManager()

    # Instantiate view and controllers, as well as registering them
    # as listeners in event_manager
    model = Model(event_manager)
    view = PrintView(event_manager)
    state = StateController(event_manager) 

    state.run()

main()
