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


class session:
    ASIA = ['08:00:00','14:00:00']
    LONDON = ['14:00:00','20:00:00']
    NY = ['20:00:00','23:59:59']
    ALL = ['00:00:00','23:59:59']
    


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
    
    for cnt in range(total_candle, 0, -1):        
        print(cnt)           
        ohlc = broker1.get_OHLC(symbols, tf , cnt)
           
        for i in range(len(symbols)): 
            data = [ohlc[i].timestamp, ohlc[i].symbol, ohlc[i].open, ohlc[i].high, ohlc[i].low, ohlc[i].close]
            df[i].loc[cnt]= data
            
    return df

def check_for_stationarity(X, cutoff=0.05):

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

class Spread:
    i1 = None
    i2 = None
    x1 = None
    x2 = None
    Z = None
    b = None

def get_Spread( pair_index_1, pair_index_2, filtTime_df):
    
    spread = Spread()
    
# verify the cointegrated pairs
        
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
    
    #************************ Calculate Beta and Spread ***************************
    
    # compute Beta
    x1 = sm.add_constant(x1)
    results = sm.OLS(x2, x1).fit()
    
    # remove constant column
    x1 = x1[symb[pair_index_1]]
    x2 = x2[symb[pair_index_2]]
    
    #results.params
    
    b = results.params[symb[pair_index_1]]
    Z = x2 - b * x1
    Z.name = 'Spread'
    
    spread.i1 = pair_index_1
    spread.i2 = pair_index_2
    spread.x1 = x1
    spread.x2 = x2
    spread.b = b
    spread.Z = Z
    
    return spread


def Analyze_Data( start, end, time, price_df, symb):
    
    #**************************** Filter by date *************************************
    
    start_date = datetime.strptime(start, '%Y-%m-%d' )
    end_date = datetime.strptime(end, '%Y-%m-%d' )    
    
    #filter daye   
    filtDate_df =[]
    for price in price_df:
        filtDate_df.append(price.loc[(price.dt_MY.dt.date >= start_date.date()) & (price.dt_MY.dt.date <= end_date.date())])
        
    #************************* Filter by time *************************************
    # filter data only during London and NY open
    
    start = time[0]
    end = time[1]           
            
    start_time = datetime.strptime(start, '%H:%M:%S' )
    end_time = datetime.strptime(end, '%H:%M:%S' )
    
    filtTime_df =[]
    for price in filtDate_df:
        filtTime_df.append(price.loc[(price.dt_MY.dt.time >= start_time.time()) & (price.dt_MY.dt.time < end_time.time())])
    
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
    
    print (pairs)
    
    
    # find pair index
    indexs = []
    for pair in pairs:
        sub_index = []
        for symbol in pair:
            sub_index.append(symb.index(symbol))
            
        indexs.append(sub_index)
    #print(indexs)    
    
    #get zpread
    datas = []
    for index in indexs:
        spread = get_Spread(index[0], index[1], filtTime_df)
        datas.append(spread)
    
    for data in datas:
        
        # check for cointegration
        score, pvalue, _ = coint(data.x1, data.x2)
        print('\n\nCointegration between ',symb[data.i1] , symb[data.i2], ' with p-value = ', pvalue)
        print('Beta (b) is ', data.b)
        
        # test for stationary
        stationary = check_for_stationarity(data.Z)
        
        #plot the z-scores
        zscore(data.Z).plot()
        plt.axhline(zscore(data.Z).mean(), color='black')
        plt.axhline(1.0, color='red', linestyle='--')
        plt.axhline(2.0, color='red', linestyle='--')
        plt.axhline(-1.0, color='green', linestyle='--')
        plt.axhline(-2.0, color='green', linestyle='--')
        plt.legend(['Spread z-score', 'Mean', '+1', '-1'])
        plt.title('tf @' + str(timeframe)+ ' between pairs ' + symb[data.i1] + ' and ' + symb[data.i2])
        plt.show()
        

def zscore(series):
    return (series - series.mean()) / np.std(series)

# ******************************************************************************************
# Parameter ********************************
total_c = 4000
timeframe = timeframe.M15
start_date ='2018-05-01'
end_date = '2018-08-25'
time = session.ALL
    

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

price_df = get_data(symb, total_c, timeframe)

#convert datetime to local datetime
local_tz = timezone('Asia/Kuala_Lumpur')
mt4_tz = timezone('GMT')

for price in price_df:
    price['dt_MY'] = price.datetime.dt.tz_localize('UTC').dt.tz_convert('Asia/Kuala_Lumpur')

Analyze_Data( start_date, end_date, time, price_df, symb)

