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
import time, pigpio, read_PWM

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

    __MAX_CW_PW = 1280.0
    __MAX_ST_PW = 1520.0
    __MAX_CCW_PW = 1720.0

    __MIN_CW_PW = 1396.0
    __MIN_ST_PW = 1480.0
    __MIN_CCW_PW = 1448.0

    def __init__(self, cPin, fPin):

        self.controlPin = cPin
        self.feedbackPin = fPin
        self.turnDirection = self.CLOCKWISE
        self.__power = 0

        self.__pi = pigpio.pi()
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)

        self.__feedbackReader = read_PWM.reader(self.__pi, self.feedbackPin)

    def __del__(self):
        if self.__pi.connected:
            self.destroy()

    def destroy(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)
        self.__feedbackReader.cancel()
        self.__pi.stop()
    
    def __calculateDutyCycle(self, pulseWidth):
        return round(((pulseWidth/(self.__PWM_PERIOD * 10 ** 6)) * 100.0), 2) 

    def __calculatePulseWidth(self):
        if(self.turnDirection is self.CLOCKWISE):
            max = self.__MAX_CW_PW
            min = self.__MIN_CW_PW
        if(self.turnDirection is self.COUNTER_CLOCKWISE):
            max = self.__MAX_CCW_PW
            min = self.__MIN_CCW_PW

        return round((min + (((max - min) / 100.0) * self.__power)), 2)

    def setPower(self, power):
        self.__power = power

    def setRotationDir(self, rotationDir):
        self.rotationDirection = rotationDir

    def run(self):
        for dc in range (500, 2501):
            self.__pi.set_servo_pulsewidth(self.controlPin, dc) # self.__calculateDutyCycle(self.__calculatePulseWidth())
            print("Pulse width: ", dc)
            time.sleep(1)

    def __getDutyCycle(self):
        return round(self.__feedbackReader.duty_cycle(), 2)

    # def calibrate(self):
    #     for i in range (0, 5000, 10):
    #         print("* -------------------- *")
    #         print("Pulse Width = ", i)
    #         print("Duty cycle = ", self.calculateDutyCycle(i))
    #         print("* -------------------- *")
    #         self.__servo.ChangeDutyCycle(self.calculateDutyCycle(i))
    #         time.sleep(0.1)

    def stop(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)