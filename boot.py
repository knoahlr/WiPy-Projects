import machine
from network import WLAN
from machine import UART, Pin, RTC
import os
import pycom
import re
import time

import time, re, socket
from network import WLAN

def getTime():
    UTC_5=5*3600
    attempts=0
    while True and attempts < 5:
        timesock=socket.socket()
        if timesock:
            try:
                timesock.connect(socket.getaddrinfo("time.nist.gov",13)[0][4])
                break
            except OSError:
                timesock.close()
                del timesock
                time.sleep(4)
                attempts += 1
                if attempts == 5:
                    pycom.heartbeat(False)
                    pycom.rgbled(0xffffff)
                    machine.reset()

    CurrentTime=timesock.recv(1024)
    print(CurrentTime)
    #Date=re.search("\d{2}-\d{2}-\d{2}",CurrentTime).group(0)
    Date=re.search("[0-9]+-[0-9]+-[0-9]+",CurrentTime).group(0)
    Time=re.search("[0-9]+:[0-9]+:([0-9]+.[0-9]+)", CurrentTime).group(0)
    if machine.reset_cause() != machine.SOFT_RESET:
        InitRTC(Date, Time)
    tm_year=int(Date.split("-")[0]) + 100 #should be number of years since 1900
    tm_yday=int(Date.split("-")[2]) - 1 #number of day since Jan 1 of that year
    tm_hour=int(Time.split(":")[0])
    tm_min=int(Time.split(":")[1]) + 1 #Nist time seems to be around a min behind and 15 secs
    tm_sec=int(Time.split(":")[2].split(" ")[0])
    print(tm_hour, tm_yday, tm_min , tm_sec)
    epoch = int((tm_min*60) + (tm_hour*3600) + (tm_yday*86400) + ((tm_year-70)*31536000) + (((tm_year-69)/4)*86400) - (((tm_year-1)/100)*86400) + (((tm_year+299)/400)*86400))
    epoch += tm_sec
    print(epoch, time.time())
    timesock.close()
    print(epoch)
    del timesock
    return epoch

def InitRTC(Date, Time):

    DateList=re.search("[0-9]+-[0-9]+-[0-9]+",Date).group(0).split("-")
    TimeList=re.search("[0-9]+:[0-9]+:([0-9]+.[0-9]+)", Time).group(0).split(":")
    Year="20"+DateList[0]
    Month=DateList[1]
    Day=DateList[2]
    Hour=TimeList[0]
    Min=TimeList[1]
    Sec=TimeList[2].split(" ")[0]
    rtc=RTC()
    rtc.init((int(Year), int(Month), int(Day), int(Hour), int(Min), int(Sec), 0, 0))


uart = UART(0, 115200)
os.dupterm(uart)
wlan = WLAN() # get current object, without changing the mode

#GatewayIDs
gateway_id="4c6b45a4-8b35-4a10-9080-abd9b912f409"
WiPygateway_id="435997a2-7590-45bb-ab1b-c110c743118e"

#httpSAS
httpSAS = "SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f4c6b45a4-8b35-4a10-9080-abd9b912f409%2fmessages&sig=6fijY7s%2bgSdiXaffEffhfUx0BWperwSxI0zGHZzNzy4%3d&se=4634217147&skn=SendAccessPolicy"
WIPYhttpSAS="SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f435997a2-7590-45bb-ab1b-c110c743118e%2fmessages&sig=OjljnACxkfjRixCOY7MUSkDL5hH8QzNfyhadKpN55mM%3d&se=4641384176&skn=SendAccessPolicy"

#Setting Pin 13 to listen in for voltage from Obstacle Avoidance sensor
InputPin=Pin("P13",Pin.OUT)

print("Machine Reset cause is ")
print(machine.reset_cause())
#if machine.reset_cause() != machine.SOFT_RESET:
wlan.init(mode=WLAN.STA)

attempts=0
while attempts < 5 and not wlan.isconnected():
    if not wlan.isconnected():
        wlan.connect('NoahS7', auth=(WLAN.WPA2, 'Playstation4'), timeout=5000)
        print(wlan.isconnected())
        print("Noah")
    time.sleep(1)
    attempts+=1

print(wlan.isconnected())
if wlan.isconnected():
    global EpochTimeAtBoot
    EpochTimeAtBoot=getTime()


#posting.DataPost((("Distance",Ultra.distance_in_cm()),),WIPYhttpSAS, WiPygateway_id)
