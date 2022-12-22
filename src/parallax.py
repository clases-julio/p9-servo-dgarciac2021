#!/usr/bin/env python3

###############################################################################
# parallax.py                                                                 #
#                                                                             #
# Authors: Ioana Carmen, Diego García                                         #
#                                                                             #
# This code will hold a class to run a Parallax Servo                         #
###############################################################################

###############################################################################
# Neccesary modules

from enum import Enum

###############################################################################
# Main program

class TurnDirection(Enum):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

class Parallax:

    def __init__(self, cPin, fPin):
        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = TurnDirection.CLOCKWISE
        self.speed = 0
