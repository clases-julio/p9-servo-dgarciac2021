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
        pulse_width = round(pulse_width)
        if pulse_width != self.__pi.get_servo_pulsewidth(self.controlPin):
                self.__pi.set_servo_pulsewidth(self.controlPin, pulse_width)

                while self.__pi.get_servo_pulsewidth(self.controlPin) != pulse_width:
                    pass

    def __getFeedbackDCBounds(self):
        factor = 1.01
        fast_pulse_width = self.__max_ccw_pw * factor
        slow_pulse_width = self.__min_ccw_pw * factor

        test_timeout = 5.0

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

        safe_stop_pulse_width = round((self.__min_cw_pw + self.__min_ccw_pw)/2)

        pulse_width_step = 1

        if rotation_dir is self.CLOCKWISE:
            pulse_width_step *= -1
        
        static_feedback_time = 1.0
        static_feedback_time_milestone = time.time()

        static_feedback_samples = []

        self.__run_and_wait(safe_stop_pulse_width)

        while time.time() - static_feedback_time_milestone < static_feedback_time:
            static_feedback_samples.append(self.getFeedbackDutyCycle())

        static_average_feedback = sum(static_feedback_samples)/len(static_feedback_samples)

        time_per_pw = 0.5
        pw_time_milestone = time.time()

        pulse_width = safe_stop_pulse_width
        print("Trying with", pulse_width, "μs pulse width...", end="\r")

        while math.isclose(self.getFeedbackDutyCycle(), static_average_feedback, abs_tol=1.0):
            self.__run_and_wait(pulse_width)

            if (time.time() - pw_time_milestone >= time_per_pw):
                pulse_width += pulse_width_step
                print("Trying with", pulse_width, "μs pulse width...", end="\r")
                pw_time_milestone = time.time()

        print("                                                                                                  ", end="\r")

        if rotation_dir is self.CLOCKWISE:
            print("Clockwise done!")
            self.__min_cw_pw = pulse_width
            self.__find_stop_boundaries(self.COUNTER_CLOCKWISE)
        elif rotation_dir is self.COUNTER_CLOCKWISE:
            print("Counter-clockwise done!")
            self.__min_ccw_pw = pulse_width

    def __find_limit_boundaries(self, rotation_dir = CLOCKWISE):

        pulse_width_step = 1

        if rotation_dir is self.CLOCKWISE:
            safe_limit_pulse_width = self.__max_cw_pw * 0.995
        elif rotation_dir is self.COUNTER_CLOCKWISE:
            pulse_width_step *= -1
            safe_limit_pulse_width = self.__max_ccw_pw * 1.005

        laps = 5
        laps_counter = 0
        lap_completed = False

        self.__run_and_wait(safe_limit_pulse_width)

        time.sleep(5)

        start_feedback_duty_cycle = self.getFeedbackDutyCycle()

        while start_feedback_duty_cycle == 0.0:
            start_feedback_duty_cycle = self.getFeedbackDutyCycle()

        start_time = time.time()

        while laps_counter < laps:
            if lap_completed is False and self.getFeedbackDutyCycle() >= start_feedback_duty_cycle:
                lap_completed = True
                laps_counter += 1
            elif lap_completed is True and self.getFeedbackDutyCycle() < start_feedback_duty_cycle:
                lap_completed = False

        average_lap_time_max_speed = (time.time() - start_time)/laps
        average_lap_time = average_lap_time_max_speed

        print("Average time per lap at maximum speed", round(average_lap_time_max_speed, 4), "s")

        pulse_width = safe_limit_pulse_width
        print("Trying with", pulse_width, "μs pulse width... (avg time per lap =", round(average_lap_time, 4), "s)", end="\r")

        laps_counter = 0
        lap_completed = False

        self.__run_and_wait(pulse_width)

        start_feedback_duty_cycle = self.getFeedbackDutyCycle()

        while start_feedback_duty_cycle == 0.0:
            start_feedback_duty_cycle = self.getFeedbackDutyCycle()

        start_time = time.time()

        while average_lap_time <= average_lap_time_max_speed + 0.015:
            if lap_completed is False and self.getFeedbackDutyCycle() >= start_feedback_duty_cycle:
                lap_completed = True
                laps_counter += 1
            elif lap_completed is True and self.getFeedbackDutyCycle() < start_feedback_duty_cycle:
                lap_completed = False

            if laps_counter >= laps:
                average_lap_time = (time.time() - start_time)/laps
                pulse_width += pulse_width_step
                print("Trying with", pulse_width, "μs pulse width... (avg time per lap =", round(average_lap_time, 4), "s)", end="\r")
                laps_counter = 0
                self.__run_and_wait(pulse_width)
                start_time = time.time()
                start_feedback_duty_cycle = self.getFeedbackDutyCycle()
                lap_completed = False

        print("                                                                                                  ", end="\r")

        if rotation_dir is self.CLOCKWISE:
            print("Clockwise done!")
            self.__max_cw_pw = pulse_width - pulse_width_step
            self.__find_limit_boundaries(self.COUNTER_CLOCKWISE)
        elif rotation_dir is self.COUNTER_CLOCKWISE:
            print("Counter-clockwise done!")
            self.__max_ccw_pw = pulse_width - pulse_width_step




    def calibrate(self):

        print("Starting calibration procedure...", end="\n\n")

        start_timestamp = time.time()

        #self.__getFeedbackDCBounds()

        print("Minimum feedback signal duty cycle readed:", self.__min_fb_dc, "%")
        print("Maximum feedback signal duty cycle readed:", self.__max_fb_dc, "%", end="\n\n")

        print("Finding stop boundaries...")

        #self.__find_stop_boundaries()

        print("Stop boundaries found!")

        print("Pulse width for minimum speed clockwise:", self.__min_cw_pw, "μs")
        print("Pulse width for minimum speed counter-clockwise:", self.__min_ccw_pw, "μs", end="\n\n")

        print("Finding limit boundaries...")

        self.__find_limit_boundaries()

        print("Limit boundaries found!")

        print("Pulse width for maximum speed clockwise:", self.__max_cw_pw, "μs")
        print("Pulse width for maximum speed counter-clockwise:", self.__max_ccw_pw, "μs", end="\n\n")

        print("Calibration time:", round(time.time() - start_timestamp, 1), "s")