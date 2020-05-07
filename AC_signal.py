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
spi.max_speed_hz = 10000

df = pd.DataFrame()
df_temp = pd.DataFrame()
df_meta = pd.DataFrame()

def signal_read():
    GPIO.output(TFS, GPIO.LOW)
    time.sleep(5e-6)
    bytes_read = spi.readbytes(3)
    GPIO.output(TFS, GPIO.HIGH)
    
    bytes_int = int((bytes_read[2] + 256*bytes_read[1] + 65536*bytes_read[0])/64)
    bytes_hex = hex(bytes_int)
    
    voltage = 3.815e-5 * bytes_int
    if voltage > 5: voltage = voltage - 10
    
    global df_temp
    
    df_temp = pd.DataFrame({'time': [dt.datetime.now()],
                            'hex': [bytes_hex],
                            'int': [bytes_int],
                            'voltage': [voltage]})
    df_temp = df_temp.set_index('time')
    
    global df_meta
    
    try:
        df_meta = df.drop(['hex', 'int'], axis=1).resample('5S').mean()
        df_meta = df_meta.rename(columns={'voltage': 'Vavg'})
        df_meta['Vrms'] = df_meta['Vavg'].mul(m.pi/(2*m.sqrt(2)))
    except:
        pass
    
    print(df_temp)

class Counter():
    def __init__(self, increment):
        self.next_t = time.time()
        self.i=0
        self.done=False
        self.increment = increment
        self.run()

    def run(self):
        global df
        
        signal_read()
        
        if self.i > 1:
            df = df.append(df_temp)
            
        self.next_t+=self.increment
        self.i+=1
        
        if not self.done:
            threading.Timer( self.next_t - time.time(), self.run).start()

    def stop(self):
        self.done=True

a=Counter(increment = 0.001)
time.sleep(120)
a.stop()

df.to_csv(r'/home/pi/Desktop/voltagedata/rawdata.csv', index=True)
df_meta.to_csv(r'/home/pi/Desktop/voltagedata/metadata.csv', index=True)

fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(df.index, df['voltage'])
ax1.set_title('Real time voltage')

ax2.plot(df_meta.index, df_meta['Vrms'])
ax2.set_title('Vrms value')

plt.show()