# main.py -- put your code here!
import socket
import os 
import time
import pycom
import re
import posting

def InitRTC(CurrentTime):
    pycom.rgbled(0x0000ff)
    DateList=re.search("[0-9]+-[0-9]+-[0-9]+",CurrentTime).group(0).split("-")
    TimeList=re.search("[0-9]+:[0-9]+:([0-9]+.[0-9]+)", CurrentTime).group(0).split(":")
    timeTuple=(int("20"+DateList[0]), int(DateList[1]), int(DateList[2]), int(TimeList[0]), int(TimeList[1]), int(TimeList[2].split(" ")[0]), 0, 0)
    rtc=RTC()
    rtc.init(timeTuple)

def getTime():
    pycom.heartbeat(False)
    pycom.rgbled(0xff00)
    time.sleep(4)

    attempts=0
    while True and attempts < 5:
        timesock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            timesock.connect(socket.getaddrinfo('time.nist.gov',13)[0][-1])
            break
        except Exception as e:
            print(e)
            timesock.close()
            del timesock
            time.sleep_ms(100)
            attempts += 1
            if attempts == 3:
                machine.reset()
    CurrentTime=timesock.recv(1024)
    print(CurrentTime)
    InitRTC(CurrentTime)

#initializing Ultrasonic Sensors
print("Initializing Ultrasound")
Ultra=Ultrasonic.Ultrasound("P12","P14")

Start=time.ticks_ms()
while True:
    if wlan.isconnected():
        getTime()
        pycom.heartbeat(True)
        break
    End=time.ticks_ms()
    if time.ticks_diff(Start,End) > 5000:
        pycom.rgbled(0xff0000)
        print("No WiFI connection, time has not been set")
        break


    
