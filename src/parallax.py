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
import pigpio

###############################################################################
# Main program

class TurnDirection(Enum):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

class Parallax:

    _servo = pigpio.pi()

    def __init__(self, cPin, fPin):
        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = TurnDirection.CLOCKWISE
        self.speed = 0

    def run(self):
        self._servo.miServo.set_servo_pulsewidth(self.controlPin, 1720)
