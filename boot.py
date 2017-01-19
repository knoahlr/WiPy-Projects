import machine
from network import WLAN
from machine import UART
import os
import pycom
import re
import time

uart = UART(0, 115200)
os.dupterm(uart)

wlan = WLAN() # get current object, without changing the mode

if machine.reset_cause() != machine.reset:
    wlan.init(mode=WLAN.STA)
    # configuration below MUST match your home router settings!!
    #wlan.ifconfig(config=("192.168.4.1","255.255.255.0","192.168.4.1",'8.8.8.8'))
attempts=0
while attempts < 5 and not wlan.isconnected():
    #NetworksAvailable=wlan.scan()
    # change the line below to match your network ssid, security and password
    # for line in NetworksAvailable:
    #     if re.search("EWA@GUEST",line[0]):
    #         wlan.connect("EWA@GUEST", auth=(WLAN.WPA2, 'Aggrx2y085213'), timeout=5000)
            

    if not wlan.isconnected():
        wlan.connect('NoahS7', auth=(WLAN.WPA2, 'Playstation4'), timeout=5000)
    time.sleep(3)
    attempts+=1




