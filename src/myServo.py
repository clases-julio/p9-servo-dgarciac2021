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
import RPi.GPIO as GPIO
import time
import parallax

###############################################################################
# Pinout management

GPIO.setmode(GPIO.BCM)

control_pin = 4
feedback_pin = 14

GPIO.setup(control_pin, GPIO.OUT)
GPIO.setup(feedback_pin, GPIO.OUT)

###############################################################################
# Pinout initialization

GPIO.output(control_pin, GPIO.LOW)
GPIO.output(feedback_pin, GPIO.LOW)

###############################################################################
# Global variables

myParallax = parallax.Parallax(control_pin, feedback_pin)

###############################################################################
# Global methods

def callbackExit(signal, frame): # signal and frame when the interrupt was executed.
    GPIO.cleanup() # Clean GPIO resources before exit.
    sys.exit(0)

###############################################################################
# Main program

if __name__ == '__main__':
    print(myParallax.controlPin)
    print(myParallax.feedbackPin)
    while True:

        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
