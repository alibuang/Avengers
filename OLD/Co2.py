from mt4zmq import broker_class as bk
import numpy as np
import pandas as pd

import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

import matplotlib.pyplot as plt

class timeframe:
    Current = 0
    M1= 1
    M5= 5
    M15= 15
    M30= 30
    H1= 60
    H4= 240
    Daily= 1440
    Weekly = 10080
    Monthly = 43200
    
def get_close(symbols, tf,  total_candle):
    
    prices = [[],[]]
    tms = [[],[]]
    df = pd.DataFrame(columns=symbols)
    
    for cnt in range(total_candle, 0, -1):        
        print(cnt)           
        ohlc = broker1.get_OHLC(symbols, tf , cnt)
           
        for i in range(len(symbols)):        
            prices[i].append(ohlc[i].close)
            tms[i].append(ohlc[i].timestamp)
            
    return prices, tms
       

magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_1 = 'tcp://'+ ip_add_1

broker1 = bk(ip_1, magic_number)

broker1.get_acct_info()
print(broker1.company)



# ******************************************************
symbols = ['EURUSD.lmx','GBPUSD.lmx']
total_candle = 2000
tf = timeframe.Daily


prices, tms = get_close(symbols, tf,  total_candle)


# ******************************************************
X1 = pd.Series( prices[0])
X2 = pd.Series( prices[1])

X1.name = symbols[0]
X2.name = symbols[1]

print(coint(X1, X2))
#
#
#plt.plot(tms[0], X1)
#plt.plot(tms[0], X2)
#plt.xlabel('Time')
#plt.ylabel('Series Value')
#plt.legend([X1.name, X2.name]);
#plt.show()
#
#
#print(coint(X1, X2))

