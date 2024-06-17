import math
from turtle import *

def heart_a(k):
    """Calculates the x-coordinate for a heart shape based on parameter k."""
    return 15 * math.sin(k) ** 3

def heart_b(k):
    """Calculates the y-coordinate for a heart shape based on parameter k."""
    return 12 * math.cos(k) - 5 * math.cos(2 * k) - 2 * math.cos(3 * k) - math.cos(4 * k)

# Set up the turtle graphics window
speed(50000)  # Set drawing speed to fastest
bgcolor("black")  # Set background color to black

# Draw the heart shape
pensize(2)  # Set pen thickness for better visibility

for i in range(6000):
    goto(heart_a(i)*20, heart_b(i)*20)
    for j in range(5):
        color('red')
    goto(0,0)

# Hide the turtle and keep the window open
hideturtle()
done()
