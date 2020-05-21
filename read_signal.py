import RPi.GPIO as GPIO
import time, threading
import spidev

import pandas as pd
import datetime as dt
import math as m

import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TFS = 12
DRO = 23
SCLK = 24

GPIO.setup(TFS, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DRO, GPIO.IN)
GPIO.setup(SCLK, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 100000

datelist = []
voltlist = []

def signal_read():
    GPIO.output(TFS, GPIO.LOW)
    time.sleep(5e-6)
    bytes_read = spi.readbytes(3)
    GPIO.output(TFS, GPIO.HIGH)
    
    bytes_int = int((bytes_read[2] + 256*bytes_read[1] + 65536*bytes_read[0])/64)
    
    voltage = 3.815e-5 * bytes_int
    if voltage > 5: voltage = voltage - 10
    
    return voltage

class Counter():
    def __init__(self, increment):
        self.next_t = time.time()
        self.i=0
        self.done=False
        self.increment = increment
        self.run()

    def run(self):
        global datelist
        global voltlist
        
        voltlist.append(signal_read())        
        datelist.append(self.next_t)
        
        self.next_t+=self.increment
        self.i+=1

        if not self.done:
            threading.Timer( self.next_t - time.time(), self.run).start()

    def stop(self):
        self.done=True

a=Counter(increment = 0.0005)
time.sleep(10)
a.stop()

df = pd.DataFrame(list(zip(datelist, voltlist)), columns=['time', 'voltage'])

df['steptime'] = df['time'] - df['time'].shift(1)
#df['steptime'] = df['steptime'].dt.total_seconds()
#time.strftime('%Y-%m-%d %H:%M:%S.%z', time.localtime(time.time()))

df.to_csv(r'/home/pi/Desktop/voltagedata/rawdata.csv', index=True)

plt.plot(df['time'], df['voltage'])
plt.show()