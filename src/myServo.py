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
import sys
import parallax
import RPi.GPIO as GPIO

###############################################################################
# Pinout management

control_pin = 14
feedback_pin = 15

###############################################################################
# Global variables

myParallax = parallax.Parallax(control_pin, feedback_pin)

###############################################################################
# Global methods

def callbackExit(signal, frame): # signal and frame when the interrupt was executed.
    GPIO.cleanup()
    sys.exit(0)

###############################################################################
# Main program

if __name__ == '__main__':

    myParallax.run()

    while True:
        myParallax.seePS()
        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
