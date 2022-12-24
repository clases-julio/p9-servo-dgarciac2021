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
import itertools
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
    
    def __calculateDutyCycle(self, pulse_width):
        return round(((pulse_width/(self.__PWM_PERIOD * 10 ** 6)) * 100.0), 2) 

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

    def setRotationDir(self, rotation_dir):
        self.rotationDirection = rotation_dir

    def run(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, self.__calculateDutyCycle(self.__calculatePulseWidth()))

    def __getDutyCycle(self):
        return round(self.__feedbackReader.duty_cycle(), 2)

    def getFeedbackDCBounds(self):
        pw = self.__MAX_CW_PW * 0.95
        max_dc = 0.0
        min_dc = 100.0

        if pw != self.__pi.get_servo_pulsewidth(self.controlPin):
                self.__pi.set_servo_pulsewidth(self.controlPin, pw)
                while self.__pi.get_servo_pulsewidth(self.controlPin) != pw:
                    continue
        
        time_milestone = time.time()

        while time.time() - time_milestone < 10.0:
            feedback_sample = round(self.__feedbackReader.duty_cycle(), 2)
            if feedback_sample != 0.0:
                if feedback_sample < 15.0 or feedback_sample > 95.0:
                    self.__pi.set_servo_pulsewidth(self.controlPin, 1450)
                else:
                    self.__pi.set_servo_pulsewidth(self.controlPin, pw)
                if feedback_sample > max_dc:
                    max_dc = feedback_sample
                elif feedback_sample < min_dc:
                    min_dc = feedback_sample
        
        print(min_dc, max_dc)
        exit(0)

    def calibrate(self):
        
        self.getFeedbackDCBounds()

        pw_step = 10
        min_pw = self.__MAX_CW_PW - 100.0
        max_pw = self.__MAX_CCW_PW + 100.0
        pw = min_pw
        
        sample_time_per_pw = 0.5
        time_milestone = time.time()

        pulse_width_samples = [pw]
        feedback_samples = []

        while pw <= max_pw:
            if pw != self.__pi.get_servo_pulsewidth(self.controlPin):
                self.__pi.set_servo_pulsewidth(self.controlPin, pw)
                while self.__pi.get_servo_pulsewidth(self.controlPin) != pw:
                    continue

            feedback_sample = round(self.__feedbackReader.duty_cycle(), 2)
            if feedback_sample != 0.0:
                pulse_width_samples.append(feedback_sample)

            if (time.time() - time_milestone >= sample_time_per_pw):
                pulse_width_samples = [key for key, _group in itertools.groupby(pulse_width_samples)]
                feedback_samples.append(pulse_width_samples)

                pw += pw_step
                pulse_width_samples = [pw]

                time_milestone = time.time()

    def stop(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)