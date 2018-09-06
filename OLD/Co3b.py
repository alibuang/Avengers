from mt4zmq import broker_class as bk
import numpy as np
import pandas as pd
from pytz import timezone
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from datetime import datetime
import matplotlib.pyplot as plt
from pyfinance.ols import PandasRollingOLS




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
    
def get_data(symbols, total_candle, tf):

    ohlc = broker1.get_OHLC(symbols, tf , 1)
    
    df = []
    for i in range(len(symbols)):
        df.append(pd.DataFrame(columns = ['datetime', 'symbol','open','high','low','close']))
    
    
    #df = pd.DataFrame(columns = ['datetime', 'symbol','open','high','low','close'])
    #data = [ohlc[0].timestamp, ohlc[0].symbol, ohlc[0].open, ohlc[0].high, ohlc[0].low, ohlc[0].close]
    #df[0].loc[0]= data
    
    for cnt in range(total_candle, 0, -1):        
        print(cnt)           
        ohlc = broker1.get_OHLC(symbols, tf , cnt)
           
        for i in range(len(symbols)): 
            data = [ohlc[i].timestamp, ohlc[i].symbol, ohlc[i].open, ohlc[i].high, ohlc[i].low, ohlc[i].close]
            df[i].loc[cnt]= data
            
    return df

def check_for_stationarity(X, cutoff=0.05):
    # H_0 in adfuller is unit root exists (non-stationary)
    # We must observe significant p-value to convince ourselves that the series is stationary
    pvalue = adfuller(X)[1]
    if pvalue < cutoff:
        print ('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely stationary.')
        return True
    else:
        print ('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely non-stationary.')
        return False

def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.05:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs

def zscore(series):
    return (series - series.mean()) / np.std(series)

# ******************************************************************************************
#initialization
magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_1 = 'tcp://'+ ip_add_1

broker1 = bk(ip_1, magic_number)

broker1.get_acct_info()
print(broker1.company)

#get data and put in pandas dataframe
symb = ['EURUSD.lmx','GBPUSD.lmx','AUDUSD.lmx', 'USDJPY.lmx', 'NZDUSD.lmx','USDCAD.lmx','USDCHF.lmx'\
        ,'GBPJPY.lmx','EURJPY.lmx','AUDJPY.lmx', 'NZDJPY.lmx', 'CADJPY.lmx', 'CHFJPY.lmx']
#symb = ['EURUSD.lmx','GBPUSD.lmx','AUDUSD.lmx']
total_c = 4000
timeframe = timeframe.M5
price_df = get_data(symb, total_c, timeframe)

#convert datetime to local datetime
local_tz = timezone('Asia/Kuala_Lumpur')
mt4_tz = timezone('GMT')

for price in price_df:
    price['dt_MY'] = price.datetime.dt.tz_localize('UTC').dt.tz_convert('Asia/Kuala_Lumpur')

#**************************** Filter by date *************************************
start ='2018-01-15'
end = '2018-07-21'
start_date = datetime.strptime(start, '%Y-%m-%d' )
end_date = datetime.strptime(end, '%Y-%m-%d' )    

#filter daye   
filtDate_df =[]
for price in price_df:
    filtDate_df.append(price.loc[(price.dt_MY.dt.date >= start_date.date()) & (price.dt_MY.dt.date <= end_date.date())])
    
#************************* Filter by time *************************************
# filter data only during London and NY open
start = '8:00:00'
end = '14:00:00'            
        
start_time = datetime.strptime(start, '%H:%M:%S' )
end_time = datetime.strptime(end, '%H:%M:%S' )

filtTime_df =[]
for price in filtDate_df:
    filtTime_df.append(price.loc[(price.dt_MY.dt.time >= start_time.time()) & (price.dt_MY.dt.time <= end_time.time())])

#************************ Find Cointegration Pair *****************************
# find pairs with cointegration 
close_df = pd.DataFrame()
for df in filtTime_df:    
    temp_df = pd.DataFrame(df.close)
    temp_df.rename(columns={'close':df.iloc[0].symbol}, inplace=True)
    close_df = close_df.join(temp_df, how='outer')
    
#    temp_df = pd.DataFrame(df.close, columns=[df.iloc[0].symbol])
#    close_df = close_df.join(temp_df, how='outer')

scores, pvalues, pairs = find_cointegrated_pairs(close_df)

import seaborn
seaborn.heatmap(pvalues, xticklabels=symb, yticklabels=symb, cmap='RdYlGn_r' 
                , mask = (pvalues >= 0.05), annot_kws={"size": 15}
                )
seaborn.set(font_scale=0.8)
plt.show()


print (pairs)
print ('Done !!!')

import sys
sys.exit()
    
    

# ************************* Data Massage**************************
# verify the cointegrated pairs
pair_index_1 = 10
pair_index_2 = 12

X1 = pd.Series( filtTime_df[pair_index_1].close)
X2 = pd.Series( filtTime_df[pair_index_2].close)
tms = pd.Series( filtTime_df[pair_index_1].dt_MY)

X1.name = symb[pair_index_1]
X2.name = symb[pair_index_2]

#reindex X1 and X2
x1 = X1.reset_index()
x1 = x1.drop(labels='index',axis=1)
x2 = X2.reset_index()
x2 = x2.drop(labels='index',axis=1)

'''
#***************************** MA **************************************
# Get the spread between the 2 stocks
# Calculate rolling beta coefficient
rolling_beta = PandasRollingOLS(y=x1, x=x2, window=30)
spread = x2 - rolling_beta.beta[symb[pair_index_2]] * x1
spread.name = 'spread'

#spread_mavg1 = pd.rolling_mean(spread, window=1)
spread_mavg1 = spread.rolling(window=1,center=False).mean()
spread_mavg1.name = 'spread 1d mavg'

spread_mavg30 = spread.rolling(window=30,center=False).mean()
spread_mavg30.name = 'spread 30d mavg'

plt.plot(spread_mavg1.index, spread_mavg1.values)
plt.plot(spread_mavg30.index, spread_mavg30.values)
plt.legend(['1 Day Spread MAVG', '30 Day Spread MAVG'])
plt.ylabel('Spread');
plt.show()
'''

#***************************** plot Price *************************************
#plot the pair price
'''
Y = np.arange(0,len(X1),1)
plt.plot(Y, X1)
plt.plot(Y, X2)
plt.xlabel('Time')
plt.ylabel('Series Value')
plt.legend([X1.name, X2.name]);
plt.show()
'''

#************************ Calculate Beta and Spread ***************************

# compute Beta
x1 = sm.add_constant(x1)
results = sm.OLS(x2, x1).fit()

# remove constant column
x1 = x1[symb[pair_index_1]]

#results.params

b = results.params[symb[pair_index_1]]
Z = x2 - b * x1
Z.name = 'Spread'

#Y = np.arange(0,len(Z),1)
mean = np.mean(Z)

#**************************** plot spread *************************************
#plt.plot(Y, Z)
Z.plot()
plt.hlines(mean, 0, len(Y), linestyles='dashed', colors='r')
plt.xlabel('Time')
plt.ylabel('Series Value')
plt.show()

#************************** plot Z-score ************************************
#plot the z-scores
zscore(Z).plot()
#plt.plot(Y, zscore(Z))
plt.axhline(zscore(Z).mean(), color='black')
plt.axhline(1.0, color='red', linestyle='--')
plt.axhline(-1.0, color='green', linestyle='--')
plt.legend(['Spread z-score', 'Mean', '+1', '-1'])
plt.show()


#*************************** Validate ****************************************
# test for stationary
stationary = check_for_stationarity(Z)

# check for cointegration
score, pvalue, _ = coint(x1, x2)
print('Cointegration between ',symb[pair_index_1] , symb[pair_index_2], ' with p-value = ', pvalue)


# ************************************************************