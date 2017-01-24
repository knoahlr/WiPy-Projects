import machine
from network import WLAN
from machine import UART
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
        try:
            timesock=socket.socket()
        except OSError:#need to take care of EHOSTUNREACH excpetion as well
            if timesock:
                timesock.close()
                del timesock
            else:
                time.sleep(1)
                pass
        if timesock:
            timesock.connect(socket.getaddrinfo("time.nist.gov",13)[0][4])
            CurrentTime=timesock.recv(1024)
            if CurrentTime:
                break
            else:
                timesock.close()
                del timesock
                time.sleep(1)
                attempts += 1

    print(CurrentTime)
    #Date=re.search("\d{2}-\d{2}-\d{2}",CurrentTime).group(0)
    Date=re.search("[0-9]+-[0-9]+-[0-9]+",CurrentTime).group(0)
    Time=re.search("[0-9]+:[0-9]+:([0-9]+.[0-9]+)", CurrentTime).group(0)
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

uart = UART(0, 115200)
os.dupterm(uart)
wlan = WLAN() # get current object, without changing the mode

print("Machine Reset cause is ")
print(machine.reset_cause())
#if machine.reset_cause() != machine.SOFT_RESET:
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
        print(wlan.isconnected())
        print("Noah")
    time.sleep(1)
    attempts+=1

print(wlan.isconnected())
if wlan.isconnected():
    global EpochTimeAtBoot
    EpochTimeAtBoot=getTime()
