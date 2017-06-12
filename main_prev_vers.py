# main.py -- put your code here!
import socket
import os 
import time
import pycom
import re
import posting
from machine import RTC
import Ultrasonic
import gc


#Initialize RTC clock with time obtained from NIST servers.
#Update firmware to get automatic RTC update. More reliable
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
    timesock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    timesock.connect(socket.getaddrinfo('time.nist.gov',13)[0][-1])

    try:
        CurrentTime=timesock.recv(1024)
    except Exception as e:
        if re.search("(EHOSTUNREACH|ECONNRESET)",e):
            getTime()
            timesock.close()
            del timesock
            time.sleep_ms(100)
        else:
            pass
    print(CurrentTime)
    InitRTC(CurrentTime)

#initializing Ultrasonic Sensors
print("Initializing Ultrasound")
Ultra=Ultrasonic.Ultrasound("P12","P14")

#Initializing pin to listen for high output from  PIR sensor
InputPin=Pin(,Pin.IN)


Start=time.ticks_ms()
while True:
    if wlan.isconnected():
        getTime()
        pycom.heartbeat(True)
        break
    End=time.ticks_ms()
    if time.ticks_diff(Start,End) > 5000:
        pycom.heartbeat(False)
        pycom.rgbled(0xff0000)
        print("No WiFI connection, time has not been set")
        break

print("Sending Data")
pycom.heartbeat(False)
errorFile=open("Error.log","w")

#Continously send data when on. (If time was obtained)
while True:
    pycom.heartbeat(True)
while True:
    pycom.heartbeat(True)
    try:
        posting.DataPost((("Distance",Ultra.distance_in_cm()[0]),),WIPYhttpSAS, WiPygateway_id)
    except Exception as e:
        errorFile.write("The exception is {0}".format(str(e)))
    gc.collect()
    time.sleep_ms(10)
errorFile.close()   
pycom.heartbeat(False)
pycom.rgbled(0x0000ff)
    
    try:
        posting.DataPost((("Distance", Ultra.distance_in_cm()[0]), ), WIPYhttpSAS, WiPygateway_id)
    except Exception as e:
        errorFile.write("The exception is {0}".format(str(e))) 
    gc.collect()
    time.sleep_ms(10)

errorFile.close()   
pycom.heartbeat(False)
pycom.rgbled(0x0000ff)


