import RPi.GPIO as GPIO
import datetime as dt
import time
import spidev

import time
import pandas as pd
import datetime as dt
import math as m

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TFS = 12 #12
DRO = 23 #9
SCLK = 24 #11

GPIO.setup(TFS, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DRO, GPIO.IN)
GPIO.setup(SCLK, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 10000

starttime = time.time()

df = pd.DataFrame()

for i in range(0,300):
    GPIO.output(TFS, GPIO.LOW)
    time.sleep(5e-6)
    bytes_read = spi.readbytes(3)
    GPIO.output(TFS, GPIO.HIGH)
    
    bytes_int = int((bytes_read[2] + 256*bytes_read[1] + 65536*bytes_read[0])/64)
    bytes_hex = hex(bytes_int)
    
    voltage = 3.815e-5 * bytes_int
    if voltage > 5: voltage = voltage - 10
    
    df_temp = pd.DataFrame({'time': [dt.datetime.now()],
                            'hex': [bytes_hex],
                            'int': [bytes_int],
                            'voltage': [voltage]})
    df_temp = df_temp.set_index('time')
    
    if i != 0:
        df = df.append(df_temp)
    
        df_meta = df.drop(['hex', 'int'], axis=1).resample('5S').mean()
        df_meta = df_meta.rename(columns={'voltage': 'Vavg'})
        df_meta['Vrms'] = df_meta['Vavg'].mul(m.pi/(2*m.sqrt(2)))
    
        print(df_temp)
        df.to_csv(r'/home/pi/Desktop/voltagedata/rawdata.csv', index=True)
        df_meta.to_csv(r'/home/pi/Desktop/voltagedata/metadata.csv', index=True)
    
    time.sleep(5e-2)

spi.close()
