
import pygame
import random

#  Classes  #

class Snowflake:
    def __init__(self, xPosition, yPosition, radius, speed):
        self.x = xPosition
        self.y = yPosition
        self.r = radius
        self.speed = speed
        self.position = [self.x, self.y]

    def __str__(self):
        return('(%d, %d)' % (self.x, self.y))

    def move(self, x, y):
        self.x += x
        self.y += y



# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)

pygame.init()

# Set the width and height of the screen [width,height]
X_MAX = 1200
X_MID = X_MAX // 2
Y_MAX = 700
size=[X_MAX, Y_MAX]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("snowball: bad luck")

#Loop until the user clicks the close button.
done=False

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# This is your position
# snowball = [349, 10]

# Other snowflakes' positions
snow_position = []
for i in range(50):
    x = random.randrange(0, X_MAX)
    y = random.randrange(0, Y_MAX)
    snow_position.append([x, y])

# Speed of snowflakes
speed = 100

# def snowball(screen, x, y

counter = 0
the_size = 1

# -------- Main Program Loop -----------

while done==False:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop

    screen.fill(black)

    # Draw snowball
    #counter += 1
    #if counter > 200:
    #    the_size += 1
    #    counter == 0
    pygame.draw.circle(screen, green, [X_MID, 100], 200)

    for (index, snowflake) in enumerate(snow_position):
        pygame.draw.circle(screen, white, snowflake, 2)

        # Move other snowflakes up one pixel
        snowflake[1] -= 1

        # If snowflake moved off screen
        if snowflake[1] == 0:
            y = random.randrange(Y_MAX + 20, Y_MAX + 50)
            x = random.randrange(0, X_MAX)
            snow_position[index] = [x, y]

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # speed
    clock.tick(speed)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

