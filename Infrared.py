import machine
import Pin
import time
import os
import posting

#Class to manage PIR sensor, designed around having CPU paused until rising edge on PIR pin (corresponds
# to infrared heat found)


class Infrared:

    def init(self, infrared_pin):

        self.InputPin = pin(infrared_pin, Pin.IN)
        self.InputPin.callback(trigger=Pin.IRQ_RISING, handler=self.run)
        self.count = 0


    def run(self):

        machine.idle()
        posting.DataPost((("Distance", 1), ), WIPYhttpSAS, WiPygateway_id)
        self.humanfound()
        machine.idle()

    def humanFound():

        pycom.heartbeat(False)
        pycom.rgbled(0xff0000)
        print("{0} human(s) found".format(self.count))
        time.sleep_ms(100)


