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
import sys, tty, termios, time, pigpio
import RPi.GPIO as GPIO

###############################################################################
# Main program

class TurnDirection(Enum):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

class Parallax:

    __servo = pigpio.pi()

    def __init__(self, cPin, fPin):
        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = TurnDirection.CLOCKWISE
        self.speed = 0

        GPIO.setup(self.controlPin, GPIO.OUT)
        GPIO.setup(self.feedbackPin, GPIO.INPUT)

        GPIO.output(self.controlPin, GPIO.LOW)

    def run(self):
        self.__servo.set_servo_pulsewidth(self.controlPin, 1600)
