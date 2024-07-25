#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import threading
import time
import board
import argparse
import busio
import neopixel_spi as neopixel
from rpi_ws281x import Color
import random

#from OnOffDart_v4_Stable_2.py import *


# LED strip configuration:
NUM_PIXELS = 80        # Number of LED pixels.
START_PIXEL = 30       # First LED pixel at which dynamic effects will start
PIXEL_ORDER = neopixel.GRB
LED_PIN = 13          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 1.0  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

spi = busio.SPI(MOSI=board.MOSI_1, clock=board.SCK_1)
strip = neopixel.NeoPixel_SPI(
    spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
)

LEDRESET_EVENT = threading.Event()
STOP_LED = False



def reset_LED():
    #LEDRESET_EVENT.set()
    STOP_LED = True

def restart_reset_event_listener():
    #LEDRESET_EVENT.clear()
    STOP_LED = False



# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(NUM_PIXELS):
        #strip.setPixelColor(i, color)
        strip[(i+START_PIXEL)%NUM_PIXELS] = color
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(4):
            for i in range(0, NUM_PIXELS, 4):
                strip[(i+q+START_PIXEL)%NUM_PIXELS] = color
                #strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, NUM_PIXELS, 4):
                strip[(i+q+START_PIXEL)%NUM_PIXELS]=0


def notReady(strip):
    """display red aura around target indicating that player has to wait"""
    #LEDRESET_EVENT.clear()
    #while STOP_LED == False:
    for c in range(0,150,10):
        for i in range(0,NUM_PIXELS):
            if STOP_LED == True:
                return
            #strip.setPixelColor(i,Color(255-c,0,0))
            strip[i] = (255-c,0,0)
        strip.show()
        time.sleep(50/1000.0)
    for c in range(0,150,10):
        for i in range(0,NUM_PIXELS):
            if STOP_LED == True:
                return
            strip[i]=((100+c,0,0))
        strip.show()
        time.sleep(50/1000.0)


def readyFirstTime(strip,flashIterations):
    """display green aura signalising to throw"""
    for t in range(0,flashIterations):
        for i in range(0,NUM_PIXELS):
            if STOP_LED == True:
                return
            strip[i] = (255,255,255)
        strip.show()
        time.sleep(200.0/1000.0)
        for i in range(0,NUM_PIXELS):
            if STOP_LED == True:
                return
            strip[i] = (0,255,0)
        strip.show()
        time.sleep(200.0/1000.0)

    fade(Color(0,255,0),Color(40,40,40),1)


def ready(strip):
    for i in range(0,NUM_PIXELS):
        if STOP_LED == True:
            return
        strip[i] = (40,40,40)
    strip.show()

def playerHit(strip):
    """Indicating that player hit the target"""
    fade(Color(255,255,0),Color(40,40,40),0.2)

def playerMissed(strip):
    """Indicating that player completely missed the target"""
    fade(Color(255,0,0),Color(100,0,0),0.2)
    fade(Color(100,0,0),Color(40,40,40),0.2)

def clamping(strip):
    wait = 0.1
    fillStrip(strip,(255,0,0))
    time.sleep(wait)
    fillStrip(strip,(0,0,0))
    time.sleep(wait)
    fillStrip(strip,(255,0,0))


def bullseyeHit(strip,iterations=2):
    color = (255,255,255)
    fillStrip(strip,(0,0,0))
    for q in range(iterations):
        for i in range(0,NUM_PIXELS):
            for j in range(0,12):
                #strip[i-j] = (((8-j)/8)*color[0],((8-j)/8)*color[1],((8-j)/8)*color[2])
                strip[(i-j+START_PIXEL)%NUM_PIXELS] = (((12-j)/12)*color[0],((12-j)/12)*color[1],((12-j)/12)*color[2])
                strip[(i + j + START_PIXEL) % NUM_PIXELS] = (((12 - j) / 12) * color[0], ((12 - j) / 12) * color[1], ((12 - j) / 12) * color[2])
            strip.show()
            time.sleep(0.05)
    return



def victory(strip,duration=2):
    iterations = int(duration/0.1)
    for q in range(iterations):
        for i in range(0,NUM_PIXELS):
            num = random.random()
            if num < 0.5:
                strip[i] = (0,0,0)
            else:
                strip[i] = (255,255,255)
        strip.show()
        time.sleep(0.1)

    fillStrip(strip,(150,250,20))
    return

def loss(strip):
    fade(Color(255,0,0),Color(150,0,0),0.3)
    fade(Color(150,0,0),Color(80,25,25),1)

    return

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(NUM_PIXELS):
            #strip.setPixelColor(i, wheel((i + j) & 255))
            strip[i] = wheel((i + j) & 255)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(NUM_PIXELS):
            strip[(i+START_PIXEL)%NUM_PIXELS] = wheel((int(i * 256 / NUM_PIXELS) + j) & 255)
            #strip.setPixelColor(i, wheel((int(i * 256 / NUM_PIXELS) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(4):
            for i in range(0, NUM_PIXELS, 4):
                #strip.setPixelColor(i + q, wheel((i + j) % 255))
                strip[(i+q+START_PIXEL)%NUM_PIXELS] = wheel((i + j) % 255)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, NUM_PIXELS, 4):
                strip[(i+q+START_PIXEL)%NUM_PIXELS] = 0
                #strip.setPixelColor(i + q, 0)



#helping functions
def fillStrip(strip, color):
    for i in range(NUM_PIXELS):
        strip[i] = color
    strip.show()

def lightOnePixel(strip,index,color=(255,255,255),duration=1):
    strip[index] = color
    strip.show()
    time.sleep(duration)
    strip[index] = (0,0,0)
    strip.show()

def clearLED(strip):
    for i in range(0,NUM_PIXELS):
        strip[i] = (0,0,0)
    strip.show()

def fade(sourceColour,targetColour,duration):
    """Method that fade one color into another"""
    step_ms = 50.0/1000.0
    stepCount = int(duration/step_ms)

    rs = sourceColour.r
    gs = sourceColour.g
    bs = sourceColour.b
    #ws = sourceColour.w

    rt = targetColour.r
    gt = targetColour.g
    bt = targetColour.b
    #wt = targetColour.w

    rDelta = rt-rs
    gDelta = gt-gs
    bDelta = bt-bs
    #wDelta = wt-ws

    rStep = rDelta/stepCount
    gStep = gDelta/stepCount
    bStep = bDelta/stepCount
    #wStep = wDelta/stepCount

    for i in range(0,NUM_PIXELS):
        strip[i] = sourceColour
        #strip.setPixelColor(i,sourceColour)
    strip.show()

    for t in range(0, stepCount):
        rs += rStep
        gs += gStep
        bs += bStep
        #ws += wStep

        for i in range(0,NUM_PIXELS):
            if STOP_LED == True:
                return
            #print(rs, ' ', gs, ' ', bs, ' ', ws)
            strip[i] = Color(int(rs),int(gs),int(bs))
            #strip.setPixelColor(i,Color(int(rs),int(gs),int(bs)))
        strip.show()
        time.sleep(50.0/1000.0)


def trimColor(oldColor):
    """Set color value to 255 if it for some reason becomes higher"""
    if oldColor.r>255:
        newColor.r = 255
    if oldColor.g>255:
        newColor.g = 255
    if oldColor.b>255:
        newColor.b = 255

    return newColor



# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    args.clear = True
    # Create NeoPixel object with appropriate configuration.
    #strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    #strip.begin()


    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')


    try:
        while True:
            #print("testing red light")
            #waitForTheNextThrow(strip)
            #time.sleep(10)
            #allowedToThrow(strip,5)
            #playerHitTheTarget(strip)
            #playerMissedTheTarget(strip)

            #colorWipe(strip, (255,255,255),2)
            #theaterChaseRainbow(strip)
            #rainbowCycle(strip)
            #theaterChase(strip,(255,255,255))

            #time.sleep(2)
            #fade(Color(255,0,0),Color(0,255,0),2)
            #fade(Color(0,255,0),Color(255,0,0),2)
            #clamping(strip)
            #lightOnePixel(strip,30)
            #lightOnePixel(strip, int(random.Random()*NUM_PIXELS))
            #time.sleep(1)
            bullseyeHit(strip,2)


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
