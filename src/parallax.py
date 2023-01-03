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
# Main class

class Parallax:

    class __dir_of_rot(Enum): # Intended to hold a human-readable value
        CLOCKWISE = 0
        COUNTER_CLOCKWISE = 1

    CLOCKWISE = __dir_of_rot.CLOCKWISE
    COUNTER_CLOCKWISE = __dir_of_rot.COUNTER_CLOCKWISE

    # VALUES BELOW ARE EXTRACTED FROM SERVO'S DATASHEET #

    # CAUTION: They will be overwritten by the calibration procedure
    # (except for those values related to PWM frequency/period which will remain
    # constant)

    __min_fb_dc = 2.9
    __max_fb_dc = 97.1

    __PWM_FREQUENCY = 50
    __PWM_PERIOD = 1/__PWM_FREQUENCY

    __max_cw_pw = 1280.0
    __max_ccw_pw = 1720.0

    __min_cw_pw = 1480.0
    __min_ccw_pw = 1520.0

    # VALUES ABOVE ARE EXTRACTED FROM SERVO'S DATASHEET #

    def __init__(self, c_pin, f_pin):

        self.control_pin = c_pin
        self.feedback_pin = f_pin

        # Default turn direction will be clockwise
        # CAUTION: Speed calculations (A.K.A. pulse width) will be influenced by this value
        # since upper and lower limits might vary from one direction to another.

        self.rotation_direction = self.CLOCKWISE 

        # A linear value which normalizes the spectrum from lower to upper
        # limit from 0 (excluded) to 100 (included)

        self.__power = 0

        self.__pi = pigpio.pi()
        self.__pi.set_servo_pulsewidth(self.control_pin, 0) # Ensure that the control pin is low

        # This object will track the feedback pin

        self.__feedback_reader = read_PWM.reader(self.__pi, self.feedback_pin)

    def __del__(self):
        # Only "destroy" the object if it exists, since "destroy()" might be called before the
        # object destructor.

        if self.__pi.connected:
            self.destroy()

    def destroy(self):
        # Stops the servo and calls the default destructors of classes involved.

        self.__pi.set_servo_pulsewidth(self.control_pin, 0)
        self.__feedback_reader.cancel()
        self.__pi.stop()

    def __calculate_pulse_width(self, power):

        if power == 0: # Will return a "safe" pulse width right in the middle of the "stop "
            return round((self.__min_cw_pw + self.__min_ccw_pw) / 2)

        # The limits will vary between rotation directions,
        # and so will be the final result. This means that for the same "power" given,
        # the final pulse width will depend on the rotation direction.

        if(self.rotation_direction is self.CLOCKWISE):
            max = self.__max_cw_pw
            min = self.__min_cw_pw
        elif(self.rotation_direction is self.COUNTER_CLOCKWISE):
            max = self.__max_ccw_pw
            min = self.__min_ccw_pw
        
        # Linear approximation. According to pigpio, pulse width should be between 500-2500 μs, thus the round.
        print(min, max)
        return round((min + (((max - min) / 100.0) * power)))

    def set_power(self, power, auto_refresh = False):

        self.__power = power

        # The power attribute does not directly make changes on the real servo's speed until the next run() is called,
        # since run() takes the current power attribute to calculate the speed.
        # If "auto_refresh" is set to "True", this process is done automatically.

        if auto_refresh is True:
            self.run()

    def get_power(self):
        return self.__power

    def set_rotation_direction(self, rotation_dir):
        self.rotation_direction = rotation_dir

    def get_feedback_duty_cycle(self):
        # The reader class built on the constructor allows to read the duty cycle of the feedback pin.
        # This might be used from outside the class for positioning purposes, although it is also internally
        # used for the calibration procedure.

        return round(self.__feedback_reader.duty_cycle(), 2)

    def run(self, power = None):
        # By default, the run() method will take the power attribute to calculate the final pulse width.
        # However this might be overwritten if a power is parsed, which will overwrite the attribute itself.

        if power is not None:
            self.__power = power

        if power > 0:
            self.rotation_direction = self.CLOCKWISE
        elif power < 0:
            self.rotation_direction = self.COUNTER_CLOCKWISE

        self.__pi.set_servo_pulsewidth(self.control_pin, self.__calculate_pulse_width(self.__power))

    def stop(self):
        # Following the method calls, a procedure which will return a safe pulse width inside the "stop zone"
        # if you try to run the servo at "0" power.

        self.run(0)

    def __run_and_wait(self, pulse_width):
        # Sometimes the pulse width parsed might not be a whole number.
        pulse_width = round(pulse_width)

        # Applies the changes only when it is necessary, and waits for them to be applied before continue.
        # This is used on the calibration procedure.

        if pulse_width != self.__pi.get_servo_pulsewidth(self.control_pin):
                self.__pi.set_servo_pulsewidth(self.control_pin, pulse_width)

                while self.__pi.get_servo_pulsewidth(self.control_pin) != pulse_width:
                    pass

    def __get_feedback_dc_bounds(self):

        # Safe values where the servo speed will be close to slowest and quickest possible.
        # Counter-clockwise is choosen since both upper and lower pulse width limits will be 
        # in boundaries afther applying the factor below.

        factor = 1.01
        fast_pulse_width = self.__max_ccw_pw * factor
        slow_pulse_width = self.__min_ccw_pw * factor

        test_timeout = 15.0 # Timeout for this test.

        # Bounds used to determine the "slow zone" and "quick zone", expressed on Duty Cycle (%)

        lower_dc_bound = 30.0 
        upper_dc_bound = 80.0

        # Initializes min and max with values that will be overwritten for sure.

        min_dc = 100.0
        max_dc = 0.0

        print("Analyzing feedback signal...")

        self.__run_and_wait(fast_pulse_width)

        time_milestone = time.time() # Sets a milestone to keep track of the test time.

        while time.time() - time_milestone < test_timeout: # While the time has not expired...
            feedback_sample = round(self.__feedback_reader.duty_cycle(), 2) # Take a feedback duty cycle sample.

            if feedback_sample != 0.0: # If that sample is not zero...
                if feedback_sample < lower_dc_bound or feedback_sample > upper_dc_bound: # and its inside the "slow zone" ...
                    self.__run_and_wait(slow_pulse_width) # run the servo at low speed
                else: # and its inside the "quick zone" ...
                    self.__run_and_wait(fast_pulse_width) # run the servo at high speed

                if feedback_sample > max_dc: # If that sample is greater than the current maximum
                    max_dc = feedback_sample # Refresh the maximun with the new value. Same goes for minimum.
                elif feedback_sample < min_dc:
                    min_dc = feedback_sample

            print("Completed: ", round(((time.time() - time_milestone)*100)/test_timeout, 1), "%", end="\r")

        print("Feedback signal analyzed!") # Reach this point means that the timer set before has expired

        # Overwrite the default values with the new values found.

        self.__min_fb_dc = min_dc
        self.__max_fb_dc = max_dc

    def __find_stop_boundaries(self, rotation_dir = CLOCKWISE):

        # The approach intended is to gradually change the pulse width applied to the servo until some noticeable
        # change is readed on the feedback pin, meaning that the servo is actually moving and thus finding the minimum
        # pulse width needed to make the servo move in either direction. The starting point will be a safe stop value
        # between the minimum of both lower limits.

        safe_stop_pulse_width = round((self.__min_cw_pw + self.__min_ccw_pw)/2)

        pulse_width_step = 1 # The pulse width tested will be changed by this value each time

        if rotation_dir is self.CLOCKWISE: # The pulse width step should be negative in clockswise direction.
            pulse_width_step *= -1

        self.__run_and_wait(safe_stop_pulse_width)

        static_feedback_samples = []

        static_feedback_time = 1.0 # Time while feedback samples will be taken with the servo totally stopped in the current position.
        static_feedback_time_milestone = time.time() # Time milestone used as a timer.

        while time.time() - static_feedback_time_milestone < static_feedback_time: # Take as many samples as possible
            static_feedback_samples.append(self.get_feedback_duty_cycle())

        static_average_feedback = sum(static_feedback_samples)/len(static_feedback_samples)

        time_per_pw = 0.5 # Time while the given pulse width is tested
        pw_time_milestone = time.time()

        pulse_width = safe_stop_pulse_width
        print("Trying with", pulse_width, "μs pulse width...", end="\r")

        while math.isclose(self.get_feedback_duty_cycle(), static_average_feedback, abs_tol=1.0):
            # The hall sensor is very sensitive once the servo starts moving, so feedback samples will be taken continously
            # until there is a difference greater than a given value.

            self.__run_and_wait(pulse_width)

            if (time.time() - pw_time_milestone >= time_per_pw): # When the timer expires...
                pulse_width += pulse_width_step # Assume that the servo has not move with this pulse width and tries with next one
                print("Trying with", pulse_width, "μs pulse width...", end="\r")
                pw_time_milestone = time.time() # Resets the timer

        print("                                                                                                  ", end="\r")

        # Since this procedure should be done in both directions, recursivity is used with a parameter
        # indicating the rotation direction. Clockwise as default will be first, and then counter-clockwise.
        # If counter-clockwise is called, then the recursive call stops.

        if rotation_dir is self.CLOCKWISE:
            print("Clockwise done!")
            self.__min_cw_pw = pulse_width
            self.__find_stop_boundaries(self.COUNTER_CLOCKWISE)
        elif rotation_dir is self.COUNTER_CLOCKWISE: # 
            print("Counter-clockwise done!")
            self.__min_ccw_pw = pulse_width

    def __find_limit_boundaries(self, rotation_dir = CLOCKWISE):

        # The approach intended here is to run the servo a bit beyond its maximum limit
        # (According to the datasheet, the servo will run at maximum speed constantly if the maximum limit is surpassed)
        # then gradually reduce the pulse width until a noticeable change in axle speed is detected thanks to the feedback pin,
        # meaning that the upper limit was the value RIGHT BEFORE that pulse width has been changed.

        # The speed calculation is done by timing the servo to run over the same spot (A.K.A. the same Duty Cycle value on the feedback pin)
        # Thus determining an average time per lap. If this time por lap is increased at a given time, will mean that the servo
        # is slowing down.

        pulse_width_step = 1 # The pulse width tested will be changed by this value each time

        # Some parameters will differ from one rotation direction to another.

        if rotation_dir is self.CLOCKWISE:
            safe_limit_pulse_width = self.__max_cw_pw * 0.995 # Subtly beyond the limit
            max_pulse_width = self.__max_cw_pw
        elif rotation_dir is self.COUNTER_CLOCKWISE:
            pulse_width_step *= -1
            safe_limit_pulse_width = self.__max_ccw_pw * 1.005 # Subtly beyond the limit
            max_pulse_width = self.__max_ccw_pw

        # Lap parameters

        laps = 10
        laps_counter = 0
        lap_completed = False

        pulse_width = safe_limit_pulse_width

        self.__run_and_wait(pulse_width)

        start_feedback_duty_cycle = self.get_feedback_duty_cycle() # The "home" position will be the current position of the axle.

        # Waits until the feedback returns a number which is not zero. The reader class needs the servo to be running
        # to set some values before returning valid values, otherwise it returns 0.

        while start_feedback_duty_cycle == 0.0:
            start_feedback_duty_cycle = self.get_feedback_duty_cycle()

        # Timer parameters

        avg_time_laps_at_max = []
        average_lap_time_max_speed = None

        start_time = time.time()

        while True: # The loop will be broken eventually
            # The duty cycle loops between 0 and 100% (Actually the real limits are set on the datahseet/calibration procedure)
            # The start point will be randomly at any value between those limits. Reading values above or below this position
            # could mean a full lap. A flag is set as soon as the first value above the start position is readed,
            # and reseted as soon as the first value below the start position is readed. This "flanges" are count as one lap.

            if lap_completed is False and self.get_feedback_duty_cycle() >= start_feedback_duty_cycle:
                lap_completed = True
                laps_counter += 1
            elif lap_completed is True and self.get_feedback_duty_cycle() < start_feedback_duty_cycle:
                lap_completed = False

            if laps_counter == laps - 1: # Once the target laps are reached...
                average_lap_time = (time.time() - start_time)/laps # The time per one lap is calculated

                # All lap times are taken to calculate a median until the tested pulse width reaches the 
                # theoretical maximum (Remember that the test started subtly beyond this maximum), then the lap time
                # is compared to this median. Once the lap time increseases by a certain value, the loop is broken.

                if round(pulse_width) == round(max_pulse_width) and average_lap_time_max_speed is None:
                    avg_time_laps_at_max.append(average_lap_time)
                    average_lap_time_max_speed = sum(avg_time_laps_at_max)/len(avg_time_laps_at_max)
                    print("avg time per lap at maximun speed:", round(average_lap_time_max_speed, 4), "s")
                elif average_lap_time_max_speed is not None and average_lap_time/average_lap_time_max_speed >= 1.03: break

                # If the loop is not broken by this line, then means that the speed remains constant and thus the next
                # pulse width is being prepared.

                # Resets lap parameters.

                pulse_width += pulse_width_step
                laps_counter = 0
                lap_completed = False

                if average_lap_time_max_speed is not None:
                    print("(avg time per lap =", round(average_lap_time, 4), "s)", "Trying with", round(pulse_width), "μs pulse width...", end="\r")
                
                self.__run_and_wait(pulse_width)
                
                start_feedback_duty_cycle = self.get_feedback_duty_cycle()
                
                while start_feedback_duty_cycle == 0.0:
                    start_feedback_duty_cycle = self.get_feedback_duty_cycle()
                
                start_time = time.time()

        print("                                                                                                  ", end="\r")

        # Since this procedure should be done in both directions, recursivity is used with a parameter
        # indicating the rotation direction. Clockwise as default will be first, and then counter-clockwise.
        # If counter-clockwise is called, then the recursive call stops.

        if rotation_dir is self.CLOCKWISE:
            print("Clockwise done!")
            self.__max_cw_pw = round(pulse_width - pulse_width_step)
            self.__find_limit_boundaries(self.COUNTER_CLOCKWISE)
        elif rotation_dir is self.COUNTER_CLOCKWISE:
            print("Counter-clockwise done!")
            self.__max_ccw_pw = round(pulse_width - pulse_width_step)

    def calibrate(self):

        print("Starting calibration procedure...", end="\n\n")

        start_timestamp = time.time()

        self.__get_feedback_dc_bounds()

        print("Minimum feedback signal duty cycle readed:", self.__min_fb_dc, "%")
        print("Maximum feedback signal duty cycle readed:", self.__max_fb_dc, "%", end="\n\n")

        print("Finding stop boundaries...")

        self.__find_stop_boundaries()

        print("Stop boundaries found!")

        print("Pulse width for minimum speed clockwise:", self.__min_cw_pw, "μs")
        print("Pulse width for minimum speed counter-clockwise:", self.__min_ccw_pw, "μs", end="\n\n")

        print("Finding limit boundaries...")

        self.__find_limit_boundaries()

        print("Limit boundaries found!")

        print("Pulse width for maximum speed clockwise:", self.__max_cw_pw, "μs")
        print("Pulse width for maximum speed counter-clockwise:", self.__max_ccw_pw, "μs", end="\n\n")

        print("Calibration time:", round(time.time() - start_timestamp, 1), "s")

        self.stop()