#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import PixelStrip, Color
import argparse

# LED strip configuration:
LED_COUNT = 5        # Number of LED pixels.
LED_PIN = 13          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def waitForTheNextThrow(strip):
    """display red aura around target indicating that player has to wait"""
    while True:
        for c in range(0,150,10):
            for i in range(0,strip.numPixels()):
                strip.setPixelColor(i,Color(255-c,0,0))
            strip.show()
            time.sleep(50/1000.0)
        for c in range(0,150,10):
            for i in range(0,strip.numPixels()):
                strip.setPixelColor(i,Color(100+c,0,0))
            strip.show()
            time.sleep(50/1000.0)
            
def fade(sourceColour,targetColour,duration):
    """Method that fade one color into another"""
    step_ms = 50.0/1000.0
    stepCount = int(duration/step_ms)
    
    rs = sourceColour.r
    gs = sourceColour.g
    bs = sourceColour.b
    
    rt = targetColour.r
    gt = targetColour.g
    bt = targetColour.b
    
    rDelta = rt-rs
    gDelta = gt-gs
    bDelta = bt-bs
    
    rStep = rDelta/stepCount
    gStep = gDelta/stepCount
    bStep = bDelta/stepCount
    
    for i in range(0,strip.numPixels()):
        strip.setPixelColor(i,sourceColour)
    strip.show()
    
    for t in range(0, stepCount):
        rs += rStep
        gs += gStep
        bs += bStep
        for i in range(0,strip.numPixels()):
            strip.setPixelColor(i,Color(int(rs),int(gs),int(bs)))
        strip.show()
        time.sleep(50.0/1000.0)
    


def allowedToThrow(strip,flashIterations):
    """display green aura signalising to throw"""
    for t in range(0,flashIterations):
        for i in range(0,strip.numPixels()):
            strip.setPixelColor(i,Color(255,255,255))
        strip.show()    
        time.sleep(200.0/1000.0)
        for i in range(0,strip.numPixels()):
            strip.setPixelColor(i,Color(0,255,0))
        strip.show()
        time.sleep(200.0/1000.0)
        
    fade(Color(0,255,0),Color(6,6,6),1)    
        
    


def playerHitTheTarget(strip):
    """Indicating that player hit the target"""
    fade(Color(60,60,0),Color(6,6,6),0.2)

def playerMissedTheTarget(strip):
    """Indicating that player completely missed the target"""
    fade(Color(100,0,0),Color(40,0,0),0.2)
    fade(Color(40,0,0),Color(6,6,6),0.2)


def bulleyeHit(strip):
    
    
def trimColor(oldColor):
    """Set color value to 255 if it for some reason becames higher"""
    if oldColor.r>255:
        newColor.r = 255
    if oldColor.g>255:
        newColor.g = 255
    if oldColor.b>255:
        newColor.b = 255
    
    return newColor

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
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

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
            playerMissedTheTarget(strip)
            time.sleep(2)
            #fade(Color(255,0,0),Color(0,255,0),2)
            #fade(Color(0,255,0),Color(255,0,0),2)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
