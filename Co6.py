from mt4zmq2 import broker_class as bk
import os
import numpy as np
import pandas as pd
from pytz import timezone
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from datetime import datetime
import matplotlib.pyplot as plt
#from pyfinance.ols import PandasRollingOLS
import telegram


class session:
    ASIA = ['08:00:00','14:00:00']
    LONDON = ['14:00:00','20:00:00']
    NY = ['20:00:00','23:59:59']
    ALL = ['00:00:00','23:59:59']
    
class trade_type:
    BUY = 0
    SELL = 1

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
    
class Spread:
    i1 = None
    i2 = None
    x1 = None
    x2 = None
    Z = None
    b = None
    stationary = None
    coi_pvalue = None
    stn_pvalue = None
    x1_signal = None
    x2_signal = None
    trade_signal = False
    x1_symbol = None
    x2_symbol = None
    
def get_data(broker, symbols, total_candle, tf):

    ohlc = broker.get_OHLC(symbols, tf , 1)
    
    df = []
    for i in range(len(symbols)):
        df.append(pd.DataFrame(columns = ['datetime', 'symbol','open','high','low','close']))
    
    for cnt in range(total_candle, 0, -1):        
        print(cnt)           
        ohlc = broker.get_OHLC(symbols, tf , cnt)
           
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

def get_Spread( index, filtTime_df):
    
    spread = Spread()
    
# verify the cointegrated pairs
        
    X1 = pd.Series( filtTime_df.iloc[:,index[0]])
    X2 = pd.Series( filtTime_df.iloc[:,index[1]])
#    tms = pd.Series( filtTime_df[pair_index_1].dt_MY)
#    print(X1, X2)
    
    X1.name = pairs[index[0]]
    X2.name = pairs[index[1]]
    
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
    x1 = x1[pairs[index[0]]]
    x2 = x2[pairs[index[1]]]
    
    #results.params
    
    b = results.params[pairs[index[0]]]
    Z = x2 - b * x1
    Z.name = 'Spread'
    
    spread.i1 = index[0]
    spread.i2 = index[1]
    spread.x1 = x1
    spread.x2 = x2
    spread.b = b
    spread.Z = Z
    
    
    
    return spread


'''
*******************************************************************************
This function is to filter the dataframe based on the start and end datetime
input parameter :
    start date : YYYY-MM-DD
    end date : YYY-MM-DD
    time: class session
    dataframe
*******************************************************************************
'''
def Filter_datetime(start_day, end_day, time, pre_df):
    
    #convert column to datetime format
    pre_df['dt_MY']=pd.to_datetime(pre_df.dt_MY)
    
    start_date = datetime.strptime(start_day, '%Y-%m-%d' )
    end_date = datetime.strptime(end_day, '%Y-%m-%d' )    
    
    start = time[0]
    end = time[1]       
    start_time = datetime.strptime(start, '%H:%M:%S' )
    end_time = datetime.strptime(end, '%H:%M:%S' )
          
    #filter dataframe based on start and end datetime
    df = pre_df.loc[(pre_df.dt_MY.dt.date >= start_date.date()) \
                    & (pre_df.dt_MY.dt.date <= end_date.date()) \
                    & (pre_df.dt_MY.dt.time >= start_time.time()) \
                    & (pre_df.dt_MY.dt.time < end_time.time())]
     
    return df
   
'''
*******************************************************************************
This function is to compile close price and datetime from a list of dataframe
to a single dataframe.
input parameter :
    dataframe
*******************************************************************************
'''
def Data_Cleaning(price_df):
    
    close_df = pd.DataFrame()
    
    for df in price_df:  

        if close_df.empty:
            temp_df = pd.DataFrame(df[['datetime','dt_MY','close']]) 
            
        else:
            temp_df = pd.DataFrame(df.close)
            
        temp_df.rename(columns={'close':df.iloc[0].symbol[:6]}, inplace=True)
        close_df = close_df.join(temp_df, how='outer')
        
    return close_df

'''
*******************************************************************************
This function is to find pair of currency that having cointegration and 
calculate the spread between them.
input parameter :
    dataframe
    list of symbols
*******************************************************************************
'''
def Prepare_Data(df_full, symb):
    
    df = df_full[symb]    
    scores, pvalues, pairs = find_cointegrated_pairs(df) 
    
    # find pair index
    indexs = []
    for pair in pairs:
        sub_index = []
        for symbol in pair:
            sub_index.append(symb.index(symbol))
            
        indexs.append(sub_index)

    print('Pair(s) having cointegration are ...')
    for i in range(len(pairs)):
        print('Pair:', pairs[i], ' Index:', indexs[i])    
    
    #get zpread
    datas = []
    for index in indexs:
#        spread = get_Spread(index[0], index[1], filtTime_df)
        spread = get_Spread(index, df)
        datas.append(spread)
        
    return datas

'''
*******************************************************************************
This function is to generate magic number based on the index number for pair
of forex pair
*******************************************************************************
'''
def Generate_MagicNumber( ix1=5, ix2=7):
    
    fro_num = 10000
    mid_num = ix1 * 100
    end_num = ix2
    
    magic_num = fro_num + mid_num + end_num
    
    return magic_num


'''
*******************************************************************************
This function is to measure the cointegration and check the stationary for the 
spread.
input parameter :
    dataframe
    list of symbols
*******************************************************************************
'''
def Analyze_Data( data):
       
    # check for cointegration
    score, pvalue, _ = coint(data.x1, data.x2) 
        
    # test for stationary
    stationary, station_pvalue = check_for_stationarity(data.Z)
    
    data.stationary = stationary
    data.coi_pvalue = pvalue
    data.stn_pvalue = station_pvalue
        
    num = '{:2.3f}'

    if pvalue < 0.05:
#    if pvalue < 0.05 and stationary and data.b > 0 and data.b < 3:
#    if pvalue < 0.05 and data.b > 0 and stationary:
        
        data.trade_signal = True
        data.x1_symbol = symb[data.i1]
        data.x2_symbol = symb[data.i2]
        
        if zscore(data.Z).iloc[-1] > 0:
            data.x1_signal = trade_type.BUY
            data.x2_signal = trade_type.SELL
        elif zscore(data.Z).iloc[-1] < 0:
            data.x1_signal = trade_type.SELL
            data.x2_signal = trade_type.BUY
            
        text1 = 'Cointegration between '+ data.x1_symbol + 'and', data.x2_symbol + 'with p-value =', num.format(data.coi_pvalue)
        text2 = 'Beta (b) is '+ num.format(data.b)
        text3 = 'Spread is stationary with pvalue '+ num.format(data.stn_pvalue)
        text4 = 'spread max = '+ num.format(zscore(data.Z).max())
        text5 = 'spread min = '+ num.format(zscore(data.Z).min())
        text6 = 'current spread value ='+ num.format(zscore(data.Z).iloc[-1])            
        print(text1,'\n',text2,'\n',text3,'\n',text4,'\n',text5,'\n',text6)
                        
    return data
            
'''
*******************************************************************************
This function is to plot Z-Score graph
input parameter :
    dataframe
*******************************************************************************
'''            
def ZPlot_Graph(data):
                    
    #plot the z-scores
    zscore(data.Z).plot()
    plt.axhline(zscore(data.Z).mean(), color='black')
    plt.axhline(1.0, color='red', linestyle='--')
    plt.axhline(2.0, color='red', linestyle='--')
    plt.axhline(-1.0, color='green', linestyle='--')
    plt.axhline(-2.0, color='green', linestyle='--')
    plt.legend(['Spread z-score', 'Mean', '+1', '-1'])
    plt.title(' between pairs ' + pairs[data.i1] + ' and ' + pairs[data.i2])
    imageFile = pairs[data.i1] + ' - ' + pairs[data.i2]
    plt.savefig( graph_dir +'\\' +imageFile +'_Z.png')
    
#    plt.show()           
    plt.clf()

def SpreadPlot_Graph(data):
                    
    #plot the z-scores
    data.Z.plot()
    plt.axhline(data.Z.mean(), color='black')
    plt.title(' between pairs ' + pairs[data.i1] + ' and ' + pairs[data.i2])
    imageFile = pairs[data.i1] + ' - ' + pairs[data.i2]
    plt.savefig( graph_dir +'\\' +imageFile +'_Spread.png')
    
#    plt.show()           
    plt.clf()

def zscore(series):
    return (series - series.mean()) / np.std(series)

'''
*******************************************************************************
                        MAIN PROGRAM
*******************************************************************************
'''

#initialization ***************************************************************
total_c = 4000
timeframe = timeframe.M15
time = session.ALL

start_date ='2018-01-01'
end_date = '2018-12-31'
    
pairs = ['EURUSD','GBPUSD','AUDUSD', 'USDJPY', 'NZDUSD','USDCAD','USDCHF'\
        ,'GBPJPY','EURJPY','AUDJPY', 'NZDJPY', 'CADJPY', 'CHFJPY']
suffixs = ['.lmx', '.']



symbols = []
for suffix in suffixs:
    symbol = []
    for pair in pairs:
        symbol.append(pair+suffix)
    symbols.append(symbol)
        
graph_dir = 'graph'
if not os.path.exists(graph_dir):
    os.makedirs(graph_dir)
    
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


# Broker
ip_add_1 = '127.0.0.100'
ip_1 = 'tcp://'+ ip_add_1
ip_add_2 = '127.0.0.101'
ip_2 = 'tcp://'+ ip_add_2
magic_number = 123456

master = bk(ip_1, magic_number)
master.get_acct_info()
slave = bk(ip_2, magic_number)
slave.get_acct_info()

print(master.company,'\n',slave.company)



# Telegram
token='488376978:AAFvFovR-Zin9VXR-AhCs0RRXXP149s_rdk'
bot = telegram.Bot(token= token)
#chat_id=-1001188026406 #R&D chat id
chat_id=-1001175571059

#send msg to telegram
#text_msg = 'Cointegration and Pair Trading'
#bot.send_message(chat_id=chat_id, text=text_msg, timeout=50)


# logic begin here ************************************************************
'''
dfs = get_data(master, symbols[0], total_c, timeframe)

#convert datetime to local datetime
local_tz = timezone('Asia/Kuala_Lumpur')
mt4_tz = timezone('GMT')

for df in dfs:
    df['dt_MY'] = df.datetime.dt.tz_localize('UTC').dt.tz_convert('Asia/Kuala_Lumpur')


closed_df = Data_Cleaning(dfs)
closed_df.to_csv(data_dir + '//' +'forex_data.csv', index=False)
'''
import sys
sys.exit()



# Read data from csv file
df = pd.read_csv(data_dir + '//' +'forex_data.csv')


new_df = Filter_datetime( start_date, end_date, time, df)
datas = Prepare_Data(new_df, pairs)

print('trade count ', slave.trade_count)
for data in datas:
    data = Analyze_Data(data)
    
    if data.coi_pvalue < 0.05 :
#    if data.coi_pvalue < 0.05 and data.b > 0 and data.stationary:
        
        ZPlot_Graph(data)
        SpreadPlot_Graph(data)
        magic_number = Generate_MagicNumber( data.i1, data.i2)
        print('magic number = ', magic_number)
        
        # 1. check if the open position exist for the pair
        slave.get_count2(magic_number, [data.x1_symbol,data.x2_symbol])
        print('trade count = ', slave.trade_count)
        
        # 2. if dont exist then open new position
        if slave.trade_count[0] == 0 and slave.trade_count[1] == 0:
            slave.get_price([data.x1_symbol, data.x2_symbol])
            
            if data.x1_signal == trade_type.BUY:
                price_x1 = slave.ask[0]
                price_x2 = slave.bid[1]
            elif data.x1_signal == trade_type.SELL:
                price_x1 = slave.bid[0]
                price_x2 = slave.ask[1]
                
            
            slave.send_order2(magic_number, data.x1_signal, data.x1_symbol, price_x1)
            slave.send_order2(magic_number, data.x2_signal, data.x2_symbol, price_x2)
            
    
#3. if open position, check magic number
magic_numbers = slave.get_opmagicnum()       
print('magic numbers are/ is ',magic_numbers)

profit_threshold = -1.00
loss_threshold = -1.00

for magic_number in magic_numbers:
    
    #4. if exist check profit / loss
    profit = slave.get_profit_by_Magic_Num(magic_number)
    print('Profit for {:6d} = {:3.2f}'.format(magic_number, profit))

    #5. if profit > 200 pip / loss > 200 pip then close position
    if profit > profit_threshold or profit < loss_threshold:
        slave.order_close_by_magicnumber(magic_number)
    
    
        

    
    