#!/usr/bin/env python3

###############################################################################
# myServo.py                                                                  #
#                                                                             #
# Authors: Ioana Carmen, Diego García                                         #
#                                                                             #
# This code will drive a Parallax Servo                                       #
###############################################################################

###############################################################################
# Neccesary modules

import signal
import sys, tty, termios
import time
import parallax

###############################################################################
# Pinout management

control_pin = 14
feedback_pin = 15

###############################################################################
# Global variables

MAX_POWER = 100
MIN_POWER = MAX_POWER * -1

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)

myParallax = parallax.Parallax(control_pin, feedback_pin)

###############################################################################
# Global methods

def callbackExit(signal, frame): # signal and frame when the interrupt was executed.
    myParallax.destroy()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
    sys.exit(0)

def draw_gauge(value):
    MAX_WIDTH = 80 - 5 - 5
    represented_value = round(MAX_WIDTH * ((value - MIN_POWER)/(MAX_POWER - MIN_POWER)))

    print("min |", end="")
    for i in range (0, represented_value):
        print(" ", end="")
    print(value, end="")
    for i in range (represented_value + len(value), MAX_WIDTH):
        print(" ", end="")
    print("| max", end="\r")


###############################################################################
# Main program

if __name__ == '__main__':

    #myParallax.calibrate()

    power = 0

    while True:

        draw_gauge(power)

        key_pressed = sys.stdin.read(1)[0]

        if key_pressed is 'a':
            if power > MIN_POWER:
                power -= 1
        elif key_pressed is 'd':
            if power < MAX_POWER:
                power += 1

        myParallax.run(power)

        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
