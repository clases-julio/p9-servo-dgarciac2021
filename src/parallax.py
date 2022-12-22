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
import time
import RPi.GPIO as GPIO

###############################################################################
# Main program

class Parallax:

    class DirOfRot(Enum):
        CLOCKWISE = 0
        COUNTER_CLOCKWISE = 1

    CLOCKWISE = DirOfRot.CLOCKWISE
    COUNTER_CLOCKWISE = DirOfRot.COUNTER_CLOCKWISE

    def __init__(self, cPin, fPin):
        GPIO.setmode(GPIO.BCM)

        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = self.CLOCKWISE
        self.speed = 0

        GPIO.setup(self.controlPin, GPIO.OUT)
        GPIO.setup(self.feedbackPin, GPIO.IN)

        self.__servo = GPIO.PWM(self.controlPin, 50) 
        self.__servo.start(0)

    def run(self):
        self.__servo.ChangeDutyCycle(8.6)