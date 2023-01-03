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
    min = -100 / 10
    max = 100 / 10

    print("min ||", end="")
    for i in range (min, value/10):
        print(" ", end="")
    print("^", end="")
    for i in range (value/10+1, max):
        print(" ", end="")
    print("|| max", end="\r")


###############################################################################
# Main program

if __name__ == '__main__':

    #myParallax.calibrate()

    power = 0

    while True:
        key_pressed = sys.stdin.read(1)[0]

        if key_pressed is 'a':
            power -= 1
        elif key_pressed is 'd':
            power += 1

        draw_gauge(power)

        myParallax.run(power)

        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
