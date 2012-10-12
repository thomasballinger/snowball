import math
import pygame
import random

#  Global Parameters  #

WIND_MAX = 10

#  Classes  #

class Snowflake:
    def __init__(self, xPosition, yPosition, radius, speed, color):
        self.x = xPosition
        self.y = yPosition
        self.r = radius
        self.speed = speed
        self.color = color
        self.area = math.pi * self.r**2

    def __str__(self):
        return('(%d, %d)' % (self.x, self.y))

    def move(self, x, y):
        self.x += x
        self.y += y

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


class Wind:
    def __init__(self, speed):
        self.speed = speed

    def change_speed(self, amount):
        new_speed = self.speed + amount
        if fabs(new_speed) <= WIND_MAX:
            self.speed += amount
        else:
            self.speed = math.copysign(WIND_MAX, new_speed)

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

# Set the width and height of the screen [width,height]
X_MAX = 1200
X_MID = X_MAX // 2
Y_MAX = 500
size=[X_MAX, Y_MAX]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("snowball: bad luck")

#Loop until the user clicks the close button.
done=False

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# This is your position
snowball = Snowflake(X_MID, 20, 10, 1, green)

# Other snowflakes' positions
snow_position = []
for i in range(500):
    x = random.randrange(0, X_MAX)
    y = random.randrange(0, Y_MAX)
    snow_position.append([x, y])

# Frames of screen
frames = 20

# def snowball(screen, x, y

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
        if event.key == pygame.K_UP:
            snowball.change_speed(1)
            print('snowball speed: %d' % snowball.speed)
        if event.key == pygame.K_DOWN:
            snowball.change_speed(-1)
            print('snowball speed: %d' % snowball.speed)

    screen.fill(black)

    # Moving snowball
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            snowball.move(-snowball.speed, 0)
            print('snowball position: %d' % snowball.x)
        if event.key == pygame.K_RIGHT:
            snowball.move(snowball.speed, 0)
            print('snowball position: %d' % snowball.x)

    # Draw snowball
    pygame.draw.circle(screen, snowball.color
                       , [snowball.x, snowball.y] , snowball.r)

    for (index, snowflake) in enumerate(snow_position):
        pygame.draw.circle(screen, white, snowflake, 2)

        # Move other snowflakes up one pixel
        snowflake[1] -= 1

        # If snowflake moved off screen
        if snowflake[1] < -20:
            y = random.randrange(Y_MAX + 20, Y_MAX + 50)
            x = random.randrange(0, X_MAX)
            snow_position[index] = [x, y]

        if collision(snowball.x, snowball.y, snowball.r, snowflake[0], snowflake[1], 1):
            snowball.area += math.pi
            print('snowball area: %d' % snowball.area)
            snowball.r = int(math.sqrt(snowball.area/math.pi))
            y = random.randrange(Y_MAX + 20, Y_MAX + 50)
            x = random.randrange(0, X_MAX)
            snow_position[index] = [x, y]

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # speed
    clock.tick(frames)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

