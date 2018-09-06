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
import telegram


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
#        print ('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely stationary.')
        return True, pvalue
    else:
#        print ('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely non-stationary.')
        return False, pvalue

def find_cointegrated_pairs(df):
#    print(df)
    n = df.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = df.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = df[keys[i]]
            S2 = df[keys[j]]
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

def get_Spread( index, filtTime_df):
    
    spread = Spread()
    
# verify the cointegrated pairs
        
    X1 = pd.Series( filtTime_df.iloc[:,index[0]])
    X2 = pd.Series( filtTime_df.iloc[:,index[1]])
#    tms = pd.Series( filtTime_df[pair_index_1].dt_MY)
#    print(X1, X2)
    
    X1.name = symb[index[0]]
    X2.name = symb[index[1]]
    
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
    x1 = x1[symb[index[0]]]
    x2 = x2[symb[index[1]]]
    
    #results.params
    
    b = results.params[symb[index[0]]]
    Z = x2 - b * x1
    Z.name = 'Spread'
    
    spread.i1 = index[0]
    spread.i2 = index[1]
    spread.x1 = x1
    spread.x2 = x2
    spread.b = b
    spread.Z = Z
    
    return spread

def Data_Cleaning( start, end, time, price_df):
    
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
        
    return close_df


def Analyze_Data(df, symb):
    
    scores, pvalues, pairs = find_cointegrated_pairs(df) 
    print (pairs) 
    
    # find pair index
    indexs = []
    for pair in pairs:
        sub_index = []
        for symbol in pair:
            sub_index.append(symb.index(symbol))
            
        indexs.append(sub_index)
    print(indexs)    
    
    #get zpread
    datas = []
    for index in indexs:
#        spread = get_Spread(index[0], index[1], filtTime_df)
        spread = get_Spread(index, df)
        datas.append(spread)
        
        
    for data in datas:
        
        # check for cointegration
        score, pvalue, _ = coint(data.x1, data.x2)       
        
        # test for stationary
        stationary, station_pvalue = check_for_stationarity(data.Z)
        
#        print (stationary, station_pvalue)
#        import sys
#        sys.exit()
        num = '{:2.3f}'
        num_100 = '{:3.0f}'
        
#        if pvalue < 0.05 and stationary:
        if pvalue < 0.05 and stationary and data.b > 0 and data.b < 3:
            
            text1 = 'Cointegration between'+ symb[data.i1] + 'and', symb[data.i2] + 'with p-value =', num.format(pvalue)
            text2 = 'Beta (b) is '+ num.format(data.b)
            text3 = 'Spread is stationary with pvalue '+ num.format(station_pvalue)
            text4 = 'spread max = '+ num.format(zscore(data.Z).max())
            text5 = 'spread min = '+ num.format(zscore(data.Z).min())
            text6 = 'current spread value ='+ num.format(zscore(data.Z).iloc[-1])
            
            print(text1)
            print(text2)
            print(text3)
            print(text4)
            print(text5)
            print(text6)
            
            lot_symb1 = 100 * data.b
            lot_symb2 = 100
            
            if zscore(data.Z).iloc[-1] > 0:
                text_signal =  'Buy ' +  symb[data.i1] + ' && Sell ' + symb[data.i2]
            elif zscore(data.Z).iloc[-1] < 0:
                text_signal =  'Sell ' +  symb[data.i1] + ' && Buy ' + symb[data.i2]
            
            timestamp = str(datetime.now().replace(microsecond=0))
            text_msg = '\n'.join([ \
                                  timestamp \
                                 ,symb[data.i1] + '(' + num_100.format(lot_symb1) +')' +' and '+ symb[data.i2] + '(' + num_100.format(lot_symb2) +')'\
                                 ,'Beta (b) is '+ num.format(data.b) \
                                 ,'current spread = ' + num.format(zscore(data.Z).iloc[-1])
                                 , text_signal
                                 ])
            bot.send_message(chat_id=chat_id, text=text_msg, timeout=500)    
            
            
                
        #plot the z-scores
            zscore(data.Z).plot()
            plt.axhline(zscore(data.Z).mean(), color='black')
            plt.axhline(1.0, color='red', linestyle='--')
            plt.axhline(2.0, color='red', linestyle='--')
            plt.axhline(-1.0, color='green', linestyle='--')
            plt.axhline(-2.0, color='green', linestyle='--')
            plt.legend(['Spread z-score', 'Mean', '+1', '-1'])
            plt.title('tf @' + str(timeframe)+ ' between pairs ' + symb[data.i1] + ' and ' + symb[data.i2])
            imageFile = symb[data.i1] + ' - ' + symb[data.i2]
            plt.savefig(imageFile +'.png')
            plt.clf()
#            plt.show()
            
            # send strength index chart to telegram
            timestamp = str(datetime.now().replace(microsecond=0))
            bot.send_photo(chat_id=chat_id, photo=open(imageFile+'.png','rb'), \
                   caption= imageFile +'\n'+timestamp, timeout=500) 
            
        

def zscore(series):
    return (series - series.mean()) / np.std(series)

# ******************************************************************************************
# ************Parameter *******************
total_c = 8000
timeframe = timeframe.M5
start_date ='2017-05-01'
end_date = '2019-08-25'
time = session.ALL
    
# Telegram
token='488376978:AAFvFovR-Zin9VXR-AhCs0RRXXP149s_rdk'
bot = telegram.Bot(token= token)
#chat_id=-1001188026406 #R&D chat id
chat_id=-1001175571059

text_msg = 'Cointegration and Pair Trading'
bot.send_message(chat_id=chat_id, text=text_msg, timeout=50)

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
    
df = Data_Cleaning(start_date, end_date, time, price_df)

df.to_csv('forex_data.csv', index=False)

data = Analyze_Data(df, symb)

