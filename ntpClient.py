

''' ######################################################################################################'''
#from machine import Pin

import time
import struct
#from machine import RTC
import socket
from socket import AF_INET, SOCK_DGRAM

#pycom.heartbeat(False)

# rtc = RTC()
# rtc.init((1970, 0, 0, 0, 0, 0, 0, 0))

def getNTPTime(host = "pool.ntp.org"):
    port = 123
    buf = 1024
    print("Stop1")
    address = socket.getaddrinfo(host,  port)[0][-1]
    print("Stop2")
    msg = '\x1b' + 47 * '\0'
    msg = msg.encode()
    TIME1970 = 2208988800 # 1970-01-01 00:00:00


    # connect to server
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.sendto(msg, address)
    print("Stop3")
    msg, address = client.recvfrom(buf)
    print(msg,address)
    t = struct.unpack("!12I", msg)[10]
    t -= TIME1970
    tuple_time = time.localtime(t)
    #rtc.init((tuple_time))
    client.close()


