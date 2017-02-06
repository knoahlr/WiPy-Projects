##
# Port of Ultrasonic library for MicroPythons pyboard by Sergio Conde Gómez.
# Port of Ultrasonic library for MicroPython's pyboard by Sergio Conde Gómez.
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
import gc

# Pin configuration.
# WARNING: Do not use PA4-X5 or PA5-X6 as the echo pin without a 1k resistor.

class Ultrasound:
    def __init__(self, tPin, ePin):
        self.triggerPin = tPin
        self.echoPin = ePin
        self.Dist_In_Cm = 0
        self.Start_Tick = 0
        self.End_Tick = 0

        # Init trigger pin (out)
        self.trigger = Pin(self.triggerPin)
        self.trigger.init(Pin.OUT)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(self.echoPin)
        self.echo.init(Pin.IN)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)
    
    def Calc_Dist(self):
        # Calc the duration of the recieved pulse, divide the result by
        # 2 (round-trip) and divide it by 29 (the speed of sound is
        # 340 m/s and that is 29 us/cm).
        self.End_Tick=time.ticks_us()
        self.Dist_In_Cm.append(((time.ticks_diff (self.Start_Tick,self.End_Tick ) / 2.0) / 29.0))

    def distance_in_cm(self):
        self.Start_Tick = 0
        self.End_Tick = 0
        self.Dist_In_Cm = []

        #Send a 10us pulse to trigger the HC-SR04
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)

        self.Start_Tick=time.ticks_us()

        self.echo.callback(Pin.IRQ_HIGH_LEVEL, Ultrasound.Calc_Dist,arg=self)
        
        time.sleep_ms(50)

        print("\n")
        print(gc.mem_free())
        print("\n")
        
        return self.Dist_In_Cm

