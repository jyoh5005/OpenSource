import os
import math
import time
 
import busio
import board #ok
 
import numpy as np
import pygame
from scipy.interpolate import griddata
 
from colour import Color
 
import adafruit_amg88xx

i2c_bus = busio.I2C(board.SCL, board.SDA)

#low range of the sensor (this will be blue on the screen)
MINTEMP = 0.
"""detect min temp"""
 
#high range of the sensor (this will be red on the screen)
MAXTEMP = 40.
"""detect max temp"""
 
#how many color values we can have
COLORDEPTH = 1024
 
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
 
#initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)
 
# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]

grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index
 
#sensor is an 8x8 grid so lets do a square
"""widows size"""
height = 480 
width = 480
 
#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))
 
#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

"""sensor detecting range"""
displayPixelWidth = width / 30
displayPixelHeight = height / 30
 
lcd = pygame.display.set_mode((width, height))
"""init lcd color""" 
lcd.fill((255, 0, 0))
 
pygame.display.update()
pygame.mouse.set_visible(False)
 
lcd.fill((0, 0, 0))
pygame.display.update()
 
#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

"""map_value(x, in_min, in_max, out_min, out_max)
    (pixel , min temp, max temp, not use, not use)"""
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
 
#let the sensor initialize
time.sleep(.1)

"""init temp infomation out to txt file"""
file = open("zxcv.txt", "w")
while True:
    #read the pixels
    """sensor's infomation convert to right the map(lcd)"""
    pixels = []
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]


    """infomation out"""
    for i in range(8):
        for n in range(8):
            file.write("%s " %pixels[i*8+n])
        file.write("\n")
    file.write("-----------------\n\n")
        
    
    #perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
 
    #draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)],
                             (displayPixelHeight * ix, displayPixelWidth * jx,
                              displayPixelHeight, displayPixelWidth))
 
    pygame.display.update()
