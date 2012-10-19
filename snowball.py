import math
import pygame
import random

#  Global Parameters  #

WIND_MAX = 10

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

def change(number, change):
    """ When given a starting number and a change amount, return the sum
    as long as the sum change signs of the starting number """
    if number < 0:
        if number + change > 0:
            return(0)
    elif number + change < 0:
        return(0)
    else:
        return(number + change)

def shift(number, change):
    number = math.copysign(change(math.fabs(number), change), number)
    return(int(number))

#  Classes  #

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
        self.x += x
        self.y += y

    def wind_move(self, xSpeed, ySpeed):
        " Movement caused by wind "
        self.x += shift(xSpeed, -self.true_area / X_DAMPEN)
        self.y += shift(ySpeed, -self.true_area / Y_DAMPEN)

    def distance_from(self, position):
        distance = math.sqrt((self.x - position[0])**2
                             + (self.y - position[1])**2)
        return(distance)

    def resize(self, amount):
        if (self.r + amount) > 0:
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
            r = random.randrange(1, 8)
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

pygame.init()


screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("snowball: bad luck")

#Loop until the user clicks the close button.
done=False

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# This is your position
snowball = Snowflake(X_MID, 20, 10, 1, green)

# Snowflake positions
snowstorm = Snowstorm(1000, SNOW_X_MIN, SNOW_X_MAX, SNOW_Y_MIN, SNOW_Y_MAX)
snowflake_positions = snowstorm.snowflakes()

# Frames of screen
frames = 30

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
#        if event.key == pygame.K_UP:
#            snowball.change_speed(1)
#            print('snowball speed: %d' % snowball.speed)
#        if event.key == pygame.K_DOWN:
#            snowball.change_speed(-1)
#            print('snowball speed: %d' % snowball.speed)

    screen.fill(black)

    # Moving snowball
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            snowball.move(0, -snowball.speed)
            print('snowball Y-position: %d' % snowball.y)
        if event.key == pygame.K_DOWN:
            snowball.move(0, snowball.speed)
            print('snowball Y-position: %d' % snowball.y)
        if event.key == pygame.K_LEFT:
            snowball.move(-snowball.speed, 0)
            print('snowball position: %d' % snowball.x)
        if event.key == pygame.K_RIGHT:
            snowball.move(snowball.speed, 0)
            print('snowball position: %d' % snowball.x)

    # Draw snowball
    pygame.draw.circle(screen, snowball.color
                       , [snowball.x, snowball.y] , snowball.r)

    # Draw snowstorm
    for (index, snowflake) in enumerate(snowflake_positions):
        pygame.draw.circle(screen, snowflake.color,
                           [snowflake.x, snowflake.y], snowflake.r)

        # Move other snowflakes up one pixel
        snowflake.move(0, -1)

        # If snowflake moved off screen
        if snowflake.y < SNOW_Y_MIN:
            x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
            y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
            r = random.randrange(1, 8)
            snowflake.x, snowflake.y, snowflake.r = x, y, r

        # If snowball and snowflake collide
        if collision(snowball.x, snowball.y, snowball.r
                     , snowflake.x, snowflake.y, snowflake.r):

            # Snowball absorbs snowflake
            snowball.area += math.pi * snowflake.r**2
            snowball.true_area += math.pi * snowflake.r**2
            print('snowball area: %d' % snowball.area)
            print('snowball true_area: %d' % snowball.true_area)
            snowball.r = int(math.sqrt(snowball.area/math.pi))
            
            # Then reset snowflake
            y = random.randrange(SNOW_Y_MAX - 5, SNOW_Y_MAX + 5)
            x = random.randrange(SNOW_X_MIN, SNOW_X_MAX)
            r = random.randrange(1, 8)
            snowflake.x, snowflake.y, snowflake.r = x, y, r

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # speed
    clock.tick(frames)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

