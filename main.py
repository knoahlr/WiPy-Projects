# main.py -- put your code here!
from time import sleep_ms

if InputPin:
    count = 0
    while True:
        print(InputPin.value())
        sleep_ms(1000)
        count += 1
        if count == 20:
            break



