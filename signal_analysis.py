import pywt
import pandas as pd
import os

df = pd.read_csv(os.getcwd() + "/thesis-rpi-sensor-signal-project/data/rawdata.csv", index_col=0)
x = df['voltage'].tolist()

cA, cD = pywt.dwt(x, 'db1')