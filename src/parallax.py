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

    class __DirOfRot(Enum):
        CLOCKWISE = 0
        COUNTER_CLOCKWISE = 1

    CLOCKWISE = __DirOfRot.CLOCKWISE
    COUNTER_CLOCKWISE = __DirOfRot.COUNTER_CLOCKWISE

    __PWM_FREQUENCY = 50
    __PWM_PERIOD = 1/__PWM_FREQUENCY

    __MAX_CW_PW = 1280
    __MAX_ST_PW = 1520
    __MAX_CCW_PW = 1720

    __MIN_CW_PW = 1479
    __MIN_ST_PW = 1480
    __MIN_CCW_PW = 1521

    def __init__(self, cPin, fPin):
        GPIO.setmode(GPIO.BCM)

        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = self.CLOCKWISE
        self.speed = 0

        GPIO.setup(self.controlPin, GPIO.OUT)
        GPIO.setup(self.feedbackPin, GPIO.IN)

        self.__servo = GPIO.PWM(self.controlPin, self.__PWM_FREQUENCY) 
        self.__servo.ChangeDutyCycle(0)
    
    def __del__(self):
        self.__servo.ChangeDutyCycle(0)
    
    def __calculateDutyCycle(self, pulseWidth):
        print(pulseWidth)
        print(self.__PWM_PERIOD * 10 ** 6)
        print(self.__calculateDutyCycle(self.__MAX_CCW_PW))
        return (pulseWidth/self.__PWM_PERIOD * 10 ** 6) * 100.0

    
    def __linearInterpolate(self):
        if(self.turnDirection is self.CLOCKWISE):
            max = self.__MAX_CW_PW
            min = self.__MIN_CW_PW
        if(self.turnDirection is self.COUNTER_CLOCKWISE):
            max = self.__MAX_CCW_PW
            min = self.__MIN_CCW_PW

    def setRotationDir(self, rotationDir):
        self.rotationDirection = rotationDir

    def run(self):
        self.__servo.ChangeDutyCycle(self.__calculateDutyCycle(self.__MAX_CCW_PW))
    
    def stop(self):
        self.__servo.ChangeDutyCycle(0)