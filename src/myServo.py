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
import time
import parallax

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
    myParallax.destroy()
    sys.exit(0)

###############################################################################
# Main program

if __name__ == '__main__':

    myParallax.run(1)

    time.sleep(5)

    myParallax.calibrate()
    
    time.sleep(5)

    myParallax.run(1)

    time.sleep(5)

    myParallax.run(100)

    time.sleep(5)

    myParallax.stop()

    while True:
        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
