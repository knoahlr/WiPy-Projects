# main.py -- put your code here!
from time import sleep_ms
import pycom

def change_color():
    pycom.heartbeat(False)
    pycom.rgbled(0xff00)

if InputPin:
    count = 0
    while True:
        machine.pin_deepsleep_wakeup(['P13'], machine.WAKEUP_ANY_HIGH, True)
        change_color()
        machine.deepsleep()
        pycom.heartbeat(True)
        count += 1
        if count == 40:
            break

print("Finished")




