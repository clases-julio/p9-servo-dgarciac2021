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
import math

###############################################################################
# Main program

class Parallax:

    class __DirOfRot(Enum):
        CLOCKWISE = 0
        COUNTER_CLOCKWISE = 1

    CLOCKWISE = __DirOfRot.CLOCKWISE
    COUNTER_CLOCKWISE = __DirOfRot.COUNTER_CLOCKWISE

    __min_fb_dc = 2.9
    __max_fb_dc = 97.1

    __PWM_FREQUENCY = 50
    __PWM_PERIOD = 1/__PWM_FREQUENCY

    __max_cw_pw = 1280.0
    __max_ccw_pw = 1720.0

    __min_cw_pw = 1480.0
    __min_ccw_pw = 1520.0

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

    def __calculatePulseWidth(self, power):
        if(self.turnDirection is self.CLOCKWISE):
            max = self.__max_cw_pw
            min = self.__min_cw_pw
        if(self.turnDirection is self.COUNTER_CLOCKWISE):
            max = self.__max_ccw_pw
            min = self.__min_ccw_pw

        return round((min + (((max - min) / 100.0) * power)), 2)

    def setPower(self, power, auto_refresh = False):
        power = round(power)
        self.__power = power
        if auto_refresh is True:
            self.run()

    def getPower(self):
        return self.__power

    def setRotationDir(self, rotation_dir):
        self.rotationDirection = rotation_dir

    def getFeedbackDutyCycle(self):
        return round(self.__feedbackReader.duty_cycle(), 2)

    def run(self, power = None):
        if power is None:
            power = self.__power

        power = round(power)
        self.__pi.set_servo_pulsewidth(self.controlPin, self.__calculateDutyCycle(self.__calculatePulseWidth(power)))

    def stop(self):
        self.__pi.set_servo_pulsewidth(self.controlPin, 0)

    def __run_and_wait(self, pulse_width):
        if pulse_width != self.__pi.get_servo_pulsewidth(self.controlPin):
                self.__pi.set_servo_pulsewidth(self.controlPin, pulse_width)

                while self.__pi.get_servo_pulsewidth(self.controlPin) != pulse_width:
                    pass

    def __getFeedbackDCBounds(self):
        factor = 1.01
        fast_pulse_width = self.__max_ccw_pw * factor
        slow_pulse_width = self.__min_ccw_pw * factor

        test_timeout = 15.0

        lower_dc_bound = 30.0
        upper_dc_bound = 80.0

        min_dc = 100.0
        max_dc = 0.0

        print("Analyzing feedback signal...")

        self.__run_and_wait(fast_pulse_width)

        time_milestone = time.time()

        while time.time() - time_milestone < test_timeout:
            feedback_sample = round(self.__feedbackReader.duty_cycle(), 2)

            if feedback_sample != 0.0:
                if feedback_sample < lower_dc_bound or feedback_sample > upper_dc_bound:
                    self.__run_and_wait(slow_pulse_width)
                else:
                    self.__run_and_wait(fast_pulse_width)

                if feedback_sample > max_dc:
                    max_dc = feedback_sample
                elif feedback_sample < min_dc:
                    min_dc = feedback_sample

            print("Completed: ", round(((time.time() - time_milestone)*100)/test_timeout, 1), "%", end="\r")

        print("Feedback signal analyzed!")
        
        self.__min_fb_dc = min_dc
        self.__max_fb_dc = max_dc
    
    def __find_stop_boundaries(self, rotation_dir = CLOCKWISE):

        pulse_width_step = 1

        safe_stop_pulse_width = (self.__min_cw_pw + self.__min_ccw_pw)/2

        if rotation_dir is self.CLOCKWISE:
            pulse_width_step *= -1
        
        static_feedback_time = 1.0
        static_feedback_time_milestone = time.time()

        static_feedback_samples = []

        self.__run_and_wait(safe_stop_pulse_width)

        while time.time() - static_feedback_time_milestone < static_feedback_time:
            static_feedback_samples.append(self.getFeedbackDutyCycle())

        print(sum(static_feedback_samples)/len(static_feedback_samples))

        exit(0)

        # time_per_pw = 0.5
        # sample_interval = time_per_pw/20
        # pw_time_milestone = time.time()
        # sample_time_milestone = time.time()

        # pulse_width_samples = []
        # pulse_width_used = []
        # feedback_samples = []
        # slope_samples = []

        # while pw <= max_pw:
        #     self.__run_and_wait(pw)

        #     if (time.time() - sample_time_milestone >= sample_interval):
        #         feedback_sample = self.__feedbackReader.duty_cycle()
        #         if feedback_sample != 0.0:
        #             pulse_width_samples.append(feedback_sample)
        #         sample_time_milestone = time.time()
            
        #     if (time.time() - pw_time_milestone >= time_per_pw):
        #         feedback_samples.append(pulse_width_samples)
        #         changes = []
        #         for x1, x2 in zip(pulse_width_samples[:-1], pulse_width_samples[1:]):
        #             try:
        #                 if math.isclose(x1, x2, abs_tol=0.55):
        #                     pct = 0.0
        #                 elif x1 < x2:
        #                     pct1 = (max_dc - x2) * 100 / x2
        #                     pct2 = (x1 - min_dc) * 100 / min_dc
        #                     pct = pct1 + pct2
        #                 else:
        #                     pct = (x2 - x1) * 100 / x1
        #             except ZeroDivisionError:
        #                 pct = 0.0
        #             changes.append(round(pct, 2))
        #         pulse_width_used.append(pw)
        #         changes = round(sum(changes) / len(changes), 2)
        #         slope_samples.append(changes)
        #         pw += pw_step
        #         pulse_width_samples = []

        #         pw_time_milestone = time.time()

        # for slope in slope_samples:
        #     if target == self.__max_cw_pw:
        #         print(pulse_width_used[slope_samples.index(slope)], ":", slope)
        #     elif target == self.__min_cw_pw:
        #         if slope == 0.0:
        #             return pulse_width_used[slope_samples.index(slope) - 1]
        #     elif target == self.__min_ccw_pw:
        #         print(pulse_width_used[slope_samples.index(slope)], ":", slope)

    def calibrate(self):

        print("Starting calibration procedure...")

        start_timestamp = time.time()
        
        self.__getFeedbackDCBounds()

        print("Minimum feedback signal duty cycle readed:", self.__min_fb_dc, "%")
        print("Maximum feedback signal duty cycle readed:", self.__max_fb_dc, "%", end="\n\n")

        print("Finding stop boundaries...")

        self.__find_stop_boundaries()

        print("Stop boundaries found!")

        print("Minimum pulse width for clockwise:", self.__min_fb_dc, "%")
        print("Maximum pulse width for counter-clockwise:", self.__max_fb_dc, "%", end="\n\n")

        # factor = 2.0
        # max_factor = 1.0 + factor/100
        # min_factor = 1.0 - factor/100

        # #self.__find_duty_cycle_boundaries(self.__max_cw_pw, self.__max_cw_pw*min_factor, self.__max_cw_pw*max_factor, min_fb_dc, max_fb_dc)
        # #print(self.__find_duty_cycle_boundaries(self.__min_cw_pw, self.__min_cw_pw*min_factor, self.__min_cw_pw*max_factor, min_fb_dc, max_fb_dc))
        # print(self.__find_duty_cycle_boundaries(self.__min_ccw_pw, self.__min_ccw_pw*max_factor, self.__min_ccw_pw*min_factor))
        # #self.__find_duty_cycle_boundaries(self.__max_ccw_pw*min_factor, self.__max_ccw_pw*max_factor)

        # print("Pulse width boundaries found!", end="\n\n")

        print("\nCalibration time:", round(time.time() - start_timestamp, 1), "s")