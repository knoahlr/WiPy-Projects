##
# Port of Ultrasonic library for MicroPythons pyboard by Sergio Conde Gómez.
# Desgined for WiPy module
# Compatible with HC-SR04 and SRF04.
#
# Copyright 2014 - Sergio Conde Gómez <skgsergio@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from machine import Pin
import time


# Pin configuration.
# WARNING: Do not use PA4-X5 or PA5-X6 as the echo pin without a 1k resistor.

class Ultrasonic:
    def __init__(self, tPin, ePin):
        self.triggerPin = tPin
        self.echoPin = ePin

        # Init trigger pin (out)
        self.trigger = Pin(self.triggerPin)
        self.trigger.init(Pin.OUT, Pin.PULL_NONE)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(self.echoPin)
        self.echo.init(Pin.IN,Pin.PULL_NONE)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)

    def distance_in_cm(self):
        start = 0
        end = 0

        # # Create a microseconds counter.
        # micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
        # micros.counter(0)


        # Send a 10us pulse.
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)

        # Wait 'till whe pulse starts.
        while self.echo.value() == 0:
            start = time.ticks_us()

        # Wait 'till the pulse is gone.
        while self.echo.value() == 1:
            end = time.ticks_us()


        # Calc the duration of the recieved pulse, divide the result by
        # 2 (round-trip) and divide it by 29 (the speed of sound is
        # 340 m/s and that is 29 us/cm).
        dist_in_cm = ((time.ticks_diff(start, end) / 2) / 29)


        return dist_in_cm