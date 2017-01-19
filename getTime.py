
import socket, time, re, ssl
UTC_5=5*3600
attempts=0

while True and attempts < 5:
    timesock=socket.socket()
    timesock.connect(socket.getaddrinfo("time.nist.gov",13)[0][4])
    CurrentTime=timesock.recv(1024)
    if CurrentTime:
        break
    else:
        timesock,close()
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
epoch = int(tm_sec + (tm_min*60) + (tm_hour*3600) + (tm_yday*86400) + ((tm_year-70)*31536000) + (((tm_year-69)/4)*86400) - (((tm_year-1)/100)*86400) + (((tm_year+299)/400)*86400))
#print(epoch, time.time())
timesock.close()
del timesock
print (epoch,time.time())
