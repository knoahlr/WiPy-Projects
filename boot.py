import machine
from network import WLAN
from machine import UART, Pin
import os

import re
import time


import time, re, socket
from network import WLAN
    
uart = UART(0, 115200)
os.dupterm(uart)
wlan = WLAN() # get current object, without changing the mode
wlan.init(mode=WLAN.STA)
for line in wlan.scan():
    #NoahWiFi=re.search("NoahS7",line[0])
    NoahWiFi=re.search("landlord50preston",line[0])

    if NoahWiFi:
        wlan.connect('landlord50preston', auth=(WLAN.WPA2, '50preston062016'), timeout=5000)
        #wlan.connect('NoahS7', auth=(WLAN.WPA2, 'Playstation4'), timeout=5000)
        time.sleep_ms(100)
        print("Connected to {0}".format(NoahWiFi.group(0)))
        time.sleep(3)
        break

if wlan.isconnected():
    rtc = machine.RTC()
    rtc.ntp_sync('pool.ntp.org')

print(rtc.now())    
#GatewayIDs
gateway_id="4c6b45a4-8b35-4a10-9080-abd9b912f409"
WiPygateway_id="435997a2-7590-45bb-ab1b-c110c743118e"

#httpSAS
httpSAS = "SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f4c6b45a4-8b35-4a10-9080-abd9b912f409%2fmessages&sig=6fijY7s%2bgSdiXaffEffhfUx0BWperwSxI0zGHZzNzy4%3d&se=4634217147&skn=SendAccessPolicy"
WIPYhttpSAS="SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f435997a2-7590-45bb-ab1b-c110c743118e%2fmessages&sig=OjljnACxkfjRixCOY7MUSkDL5hH8QzNfyhadKpN55mM%3d&se=4641384176&skn=SendAccessPolicy"

#Setting Pin 13 to listen in for voltage from Obstacle Avoidance sensor
InputPin = Pin("P13",Pin.IN)

    


#posting.DataPost((("Distance",Ultra.distance_in_cm()[0]),),WIPYhttpSAS, WiPygateway_id)
