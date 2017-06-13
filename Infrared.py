
from machine import Pin
import machine
import time
import os
import posting
import pycom
#Class to manage PIR sensor, designed around having CPU paused until rising edge on PIR pin (corresponds
# to infrared heat found)


class InfraredClass:

    WIPYhttpSAS = "SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f435997a2-7590-45bb-ab1b-c110c743118e%2fmessages&sig=OjljnACxkfjRixCOY7MUSkDL5hH8QzNfyhadKpN55mM%3d&se=4641384176&skn=SendAccessPolicy"
    WiPygateway_id = "435997a2-7590-45bb-ab1b-c110c743118e"

    def init(self, infrared_pin):

        self.InputPin = pin(infrared_pin, Pin.IN)
        self.InputPin.callback(trigger=Pin.IRQ_RISING, handler=self.run)
        self.count = 0

    def run(self):

        machine.idle()
        #print(InfraredClass.WIPYhttpSAS, InfraredClass.WiPygateway_id)
        posting.DataPost((("Distance", 1), ), InfraredClass.WIPYhttpSAS, InfraredClass.WiPygateway_id)
        self.humanFound()
        machine.idle()

    def humanFound(self):

        self.count += 1
        pycom.heartbeat(False)
        pycom.rgbled(0xff0000)
        print("{0} human(s) found".format(self.count))
        time.sleep_ms(100)


