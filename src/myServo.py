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

control_pin = 14
feedback_pin = 15

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

    myParallax.run()

    while True:
        for i in range(0, 101): 
            myParallax.power = i
            print("* -------------------- *")
            print("Power = ", myParallax.power)
            print("Pulse Width = ", myParallax.calculatePulseWidth())
            print("Duty cycle = ", myParallax.calculateDutyCycle(myParallax.calculatePulseWidth()))
            print("* -------------------- *")
            myParallax.run()
            time.sleep(0.5)
        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
