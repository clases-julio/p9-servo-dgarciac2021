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
    __MAX_CCW_PW = 1720.0

    __MIN_CW_PW = 1480.0
    __MIN_CCW_PW = 1520.0

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

    def __run_and_wait(self, pw):
        if pw != self.__pi.get_servo_pulsewidth(self.controlPin):
                self.__pi.set_servo_pulsewidth(self.controlPin, pw)
                while self.__pi.get_servo_pulsewidth(self.controlPin) != pw:
                    print("Hello?")
                    continue


    def __getFeedbackDCBounds(self):
        quick_pw = 1000
        slow_pw = 1450
        test_timeout = 3.0
        lower_dc_bound = 30.0
        upper_dc_bound = 80.0
        min_dc = 100.0
        max_dc = 0.0

        print("Analyzing feedback signal...")

        self.__run_and_wait(quick_pw)

        time_milestone = time.time()

        while time.time() - time_milestone < test_timeout:
            feedback_sample = round(self.__feedbackReader.duty_cycle(), 2)

            if feedback_sample != 0.0:
                if feedback_sample < lower_dc_bound or feedback_sample > upper_dc_bound:
                    self.__run_and_wait(slow_pw)
                else:
                    self.__run_and_wait(quick_pw)

                if feedback_sample > max_dc:
                    max_dc = feedback_sample
                elif feedback_sample < min_dc:
                    min_dc = feedback_sample

            print("Completed: ", round(((time.time() - time_milestone)*100)/test_timeout, 1), "%", end="\r")

        print("Feedback signal analyzed!")

        return min_dc, max_dc
    
    def __find_duty_cycle_boundaries(self, lower_limit, upper_limit):
        pw_step = 5
        min_pw = lower_limit
        max_pw = upper_limit
        pw = min_pw

        time_per_pw = 0.5
        sample_interval = time_per_pw/20
        pw_time_milestone = time.time()
        sample_time_milestone = time.time()

        pulse_width_samples = [pw]
        feedback_samples = []
        slope_samples = []

        while pw <= max_pw:
            self.__run_and_wait(pw)
            print(pw)

            if (time.time() - sample_time_milestone >= sample_interval):
                feedback_sample = self.__feedbackReader.duty_cycle()
                if feedback_sample != 0.0:
                    pulse_width_samples.append(feedback_sample)
                sample_time_milestone = time.time()
            
            if (time.time() - pw_time_milestone >= time_per_pw):
                feedback_samples.append(pulse_width_samples)

                changes = []
                for x1, x2 in zip(pulse_width_samples[:-1], pulse_width_samples[1:]):
                    try:
                        pct = round((x2 - x1) * 100 / x1, 2)
                    except ZeroDivisionError:
                        pct = None
                    changes.append(pct)

                slope_samples.append(changes)
                pw += pw_step
                pulse_width_samples = [pw]

                pw_time_milestone = time.time()

                print("Completed: ", round(((pw - min_pw) * 100) / (max_pw - min_pw), 1), "%", end="\r")

        for slope in slope_samples:
            index = slope_samples.index(slope)
            print(feedback_samples[index][0], ":", round(sum(slope[1:]) / len(slope[1:]), 2))

    def calibrate(self):

        print("Starting calibration procedure...")

        start_timestamp = time.time()
        
        min_fb_dc, max_fb_dc = self.__getFeedbackDCBounds()

        print("Analyzing pulse width boundaries...")

        factor = 2.0
        max_factor = 1.0 + factor/100
        min_factor = 1.0 - factor/100

        self.__find_duty_cycle_boundaries(self.__MAX_CW_PW*min_factor, self.__MAX_CW_PW*max_factor)
        self.__find_duty_cycle_boundaries(self.__MIN_CW_PW*min_factor, self.__MIN_CW_PW*max_factor)
        self.__find_duty_cycle_boundaries(self.__MIN_CCW_PW*min_factor, self.__MIN_CCW_PW*max_factor)
        self.__find_duty_cycle_boundaries(self.__MAX_CCW_PW*min_factor, self.__MAX_CW_PW*max_factor)

        print("Pulse width boundaries found!", end="\n\n")

        print("Minimum feedback signal duty cycle readed:", min_fb_dc, "%")
        print("Maximum feedback signal duty cycle readed:", max_fb_dc, "%", end="\n\n")


        print("\nCalibration time:", round(time.time() - start_timestamp, 1), "s")

    def stop(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)