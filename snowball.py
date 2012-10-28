import math
import pickle
import pygame
import random
import socket
import sys
import pygame.gfxdraw

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

class Snowstorm:
    def __init__(self, numberOfSnowflakes, xMin, xMax, yMin, yMax):
        self.intensity = numberOfSnowflakes
        self.xMin, self.xMax = xMin, xMax
        self.yMin, self.yMax = yMin, yMax

    def snowflakes(self):
        positions = []
        for i in range(self.intensity):
            x = random.randrange(self.xMin, self.xMax)
            y = random.randrange(self.yMin, self.yMax)
            r = random.randrange(1, 10)
            positions.append(Snowflake(x, y, r, 1, white))
        return(positions)


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

pygame.init()


screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("snowball: bad luck")

#Loop until the user clicks the close button.
done=False

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# This is your position
snowball = Snowflake(X_MID, 20, 2, 1, green)

# Snowflake positions
snowstorm = Snowstorm(1000, SNOW_X_MIN, SNOW_X_MAX, SNOW_Y_MIN, SNOW_Y_MAX)
snowflake_positions = snowstorm.snowflakes()

# Wind
wind = Wind(0,0)

# Frames of screen
frames = 30

# Instantiate font
font = pygame.font.Font(None, 100)

state = 'Start'
game = Game(state)

# -------- Main Program Loop -----------

while done==False:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop

    # Admin stuff
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            print('done')
            break
        if event.key == pygame.K_u:
            frames += 1
            print('frames: %d' % frames)
        if event.key == pygame.K_d:
            frames -= 1
            print('frames: %d' % frames)

    screen.fill(black)

    # Snowball Speed
    limit = min(MAX_SNOWBALL_SPEED, int(snowball.true_area // (2 * snowball.area)))
    snowball.speed = max(1, limit)

    # Moving snowball
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_UP]:
        snowball.move(0, -snowball.speed)
        print('snowball Y-position: %d' % snowball.y)
    if keys_pressed[pygame.K_DOWN]:
        snowball.move(0, snowball.speed)
        print('snowball Y-position: %d' % snowball.y)
    if keys_pressed[pygame.K_LEFT]:
        snowball.move(-snowball.speed, 0)
        print('snowball X-position: %d' % snowball.x)
    if keys_pressed[pygame.K_RIGHT]:
        snowball.move(snowball.speed, 0)
        print('snowball X-position: %d' % snowball.x)
    if keys_pressed[pygame.K_SPACE]:
        snowball.compress(snowball.area/100)
        print('snowball area: %d' % snowball.area)
        print('snowball true area: %d' % snowball.true_area)
        print('snowball radius: %d' % snowball.r)

    # Draw snowball
    pygame.gfxdraw.aacircle(screen, snowball.x, snowball.y, snowball.r, 
                            snowball.color)

    # Draw snowstorm
    for (index, snowflake) in enumerate(snowflake_positions):
        pygame.draw.circle(screen, snowflake.color,
                           [snowflake.x, snowflake.y], snowflake.r)

        # Move other snowflakes up one pixel
        snowflake.move(0, -1)

        # Apply wind
        snowflake.wind_move(wind.xSpeed, wind.ySpeed)

        # If snowflake moved off screen
        if snowflake.y < SNOW_Y_MIN:
            x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
            y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
            r = random.randrange(1, 8)
            snowflake.x, snowflake.y, snowflake.r = x, y, r

        # If snowball and snowflake collide
        if collision(snowball.x, snowball.y, snowball.r
                     , snowflake.x, snowflake.y, snowflake.r):

            if snowflake.area >= snowball.area:
                game.state = 'You Lose'
                # something else happens here

            else:
                # Snowball absorbs snowflake
                snowball.area += math.pi * snowflake.r**2
                snowball.true_area += math.pi * snowflake.r**2
                print('snowball area: %d' % snowball.area)
                print('snowball true_area: %d' % snowball.true_area)
                snowball.r = int(math.sqrt(snowball.area/math.pi))

                # Then, reset snowflake
                y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
                x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
                r = random.randrange(1, 8)
                snowflake.x, snowflake.y, snowflake.r = x, y, r

    # Check game state
    if game.state == 'You Lose':

        text = font.render(game.state, True, red)
        text_rectangle = text.get_rect()
        text_rectangle.centerx = screen.get_rect().centerx
        text_rectangle.centery = screen.get_rect().centery
        screen.blit(text, text_rectangle)

    # Update the screen with what we've drawn.
    pygame.display.flip()

    # speed
    clock.tick(frames)

pygame.quit ()

