#!/usr/bin/env python3

###############################################################################
# myServo.py                                                                  #
#                                                                             #
# Authors: Ioana Carmen, Diego García                                         #
#                                                                             #
# This code will drive a Parallax Servo                                       #
###############################################################################

###############################################################################
# Neccesary modules

import signal
import sys, tty, termios
import parallax

###############################################################################
# Pinout management

control_pin = 14
feedback_pin = 15

###############################################################################
# Global variables

MAX_POWER = 100
MIN_POWER = MAX_POWER * -1

fd = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)

myParallax = parallax.Parallax(control_pin, feedback_pin)

###############################################################################
# Global methods

def callbackExit(signal, frame): # signal and frame when the interrupt was executed.
    myParallax.destroy()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, fd)
    sys.exit(0)

def draw_gauge(value):
    start_str = "min |"
    end_str = "| max (Power: " + str(value) + "%)"

    total_char_count = 80

    max_width = total_char_count - (len(start_str) + len(end_str))

    represented_value = round(max_width * ((value - MIN_POWER)/(MAX_POWER - MIN_POWER)))

    print(start_str, end="")

    for i in range (0, max_width + 1):
        if i == represented_value:
            print("¤", end="")
        else:
            print(" ", end="")

    print(end_str, end="\r")


###############################################################################
# Main program

if __name__ == '__main__':

    myParallax.calibrate()

    print("\nServo control:\n\t- 'd' for clockwise\n\t- 'a' for counter-clockwise\n\t- 'ctrl+c' to exit\n")

    power = 0

    while True:

        draw_gauge(power)

        key_pressed = sys.stdin.read(1)[0]

        if key_pressed is 'a':
            if power > MIN_POWER:
                power -= 1
        elif key_pressed is 'd':
            if power < MAX_POWER:
                power += 1

        myParallax.run(power)

        signal.signal(signal.SIGINT, callbackExit) # callback for CTRL+C
