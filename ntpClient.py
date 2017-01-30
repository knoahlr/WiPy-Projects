#!/usr/bin/env python
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import sys
import struct
import time

NTP_PACKET_FORMAT = "!12I"
NTP_DELTA = 2208988800L # 1970-01-01 00:00:00
NTP_QUERY = '\x1b' + 47 * '\0'  

def ntp_time(host="pool.ntp.org", port=123):
        with closing(socket( AF_INET, SOCK_DGRAM)) as s:
            s.sendto(NTP_QUERY, (host, port))
            msg, address = s.recvfrom(1024)
            print msg

        unpacked = struct.unpack(NTP_PACKET_FORMAT,msg[0:struct.calcsize(NTP_PACKET_FORMAT)])
        return unpacked[10] + float(unpacked[11]) / 2**32 - NTP_DELTA


if __name__ == "__main__":
    print time.ctime(ntp_time()).replace("  "," ")


''' ######################################################################################################'''
from machine import Pin
import pycom
import utime
import ustruct
from machine import RTC
import socket
from socket import AF_INET, SOCK_DGRAM

pycom.heartbeat(False)

rtc = RTC()
rtc.init((1970, 0, 0, 0, 0, 0, 0, 0))

def getNTPTime(host = "pool.ntp.org"):
    port = 123
    buf = 1024
    address = socket.getaddrinfo(host,  port)[0][-1]
    msg = '\x1b' + 47 * '\0'
    msg = msg.encode()
    TIME1970 = 2208988800 # 1970-01-01 00:00:00

    # connect to server
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.sendto(msg, address)
    msg, address = client.recvfrom(buf)
    t = ustruct.unpack("!12I", msg)[10]
    t -= TIME1970
    tuple_time = utime.localtime(t)
    rtc.init((tuple_time))
    client.close()