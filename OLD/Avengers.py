import pandas as pd
import numpy as np
from mt4zmq import broker_class as broker
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
    
def Calculate_Abs_Strength(Isymbols, Isym_rev, cs_ohlc_0, cs_ohlc_1, prefix):
    
    symbols = Add_Prefix(Isymbols, prefix)
    sym_rev = Add_Prefix(Isym_rev, prefix)
    
    index = np.arange(len(symbols))
    df = pd.DataFrame(index=index, columns=['symbol','C0','C1'])
    
    
    found_index = None
    
    for i in range(len(symbols)):    
        df.iloc[i]['symbol'] = symbols[i]
        
        #This loop is to find the index which contain correct symbol
        for index in range(len(cs_ohlc_0)):
            if cs_ohlc_0[index].symbol == symbols[i]:
                found_index = index
                break
            elif index == len(cs_ohlc_0) and cs_ohlc_0[index].symbol != symbols[i] :
                print('Symbol Not Found')
        
#        print(cs_ohlc_0[found_index].symbol, " == ", symbols[i] )
        
        if cs_ohlc_0[found_index].symbol == symbols[i]:
            if cs_ohlc_0[found_index].symbol in sym_rev :
                df.iloc[i]['C0'] = 1 / cs_ohlc_0[found_index].close
            else:
                df.iloc[i]['C0'] = cs_ohlc_0[found_index].close
                
        if cs_ohlc_1[found_index].symbol == symbols[i]:
            if cs_ohlc_1[found_index].symbol in sym_rev :
                df.iloc[i]['C1'] = 1 / cs_ohlc_1[found_index].close
            else:
                df.iloc[i]['C1'] = cs_ohlc_1[found_index].close
                
    df['change'] = ((df['C0'] - df['C1']) / df['C1']) * 100
    
    return df

def Get_Strength_Index(timeframe, shift): 
    
    symbols = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCHF','USDCAD', \
               'EURJPY', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY','CADJPY',\
               'EURGBP', 'GBPAUD', 'GBPNZD', 'GBPCHF', 'GBPCAD', \
               'EURAUD', 'EURNZD', 'EURCHF', 'EURCAD', \
               'AUDCHF', 'AUDCAD', 'CADCHF', \
               'NZDCHF', 'NZDCAD','AUDNZD']
    symbols = Add_Prefix(symbols, prefix)
    
    sym_usd = ['EURUSD','GBPUSD','AUDUSD','NZDUSD','USDJPY','USDCHF','USDCAD']
    sym_USD_rev=['EURUSD','AUDUSD','GBPUSD','NZDUSD']
    
    sym_eur = ['EURUSD', 'EURGBP', 'EURAUD', 'EURNZD', 'EURJPY','EURCHF','EURCAD']
    sym_EUR_rev = []
    
    sym_jpy = ['USDJPY', 'GBPJPY', 'EURJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY', 'CADJPY']
    sym_JPY_rev = []
    
    sym_gbp = ['GBPUSD', 'GBPJPY', 'EURGBP', 'GBPAUD', 'GBPNZD', 'GBPCHF', 'GBPCAD']
    sym_GBP_rev = ['EURGBP']
    
    sym_aud = ['AUDUSD', 'AUDJPY', 'EURAUD', 'GBPAUD', 'AUDNZD', 'AUDCHF', 'AUDCAD']
    sym_AUD_rev = ['EURAUD', 'GBPAUD']
    
    sym_nzd = ['NZDUSD','NZDJPY','EURNZD','GBPNZD','NZDCHF','NZDCAD','AUDNZD']
    sym_NZD_rev = ['EURNZD','GBPNZD', 'AUDNZD']
    
    sym_cad = ['USDCAD','CADJPY','EURCAD','GBPCAD','NZDCAD','AUDCAD','CADCHF']
    sym_CAD_rev = ['USDCAD','EURCAD','GBPCAD','NZDCAD','AUDCAD']
    
    
    sym_chf = ['CHFJPY','USDCHF','EURCHF','GBPCHF','NZDCHF','AUDCHF','CADCHF']
    sym_CHF_rev = ['USDCHF','EURCHF','GBPCHF','NZDCHF','AUDCHF','CADCHF']
    
    cs_d1_0 = broker1.get_OHLC(symbols, timeframe , shift)
    cs_d1_1 = broker1.get_OHLC(symbols, timeframe , shift + 1)
    
    index = np.arange(8)
    strength_df = pd.DataFrame(index=index, columns=['Currency', 'ABS_strength'])
    
    USD_df = Calculate_Abs_Strength(sym_usd, sym_USD_rev, cs_d1_0, cs_d1_1, prefix)
    strength_USD = USD_df['change'].sum()
    strength_df.iloc[0]= ['USD', strength_USD]
    
    EUR_df = Calculate_Abs_Strength(sym_eur, sym_EUR_rev, cs_d1_0, cs_d1_1, prefix)
    strength_EUR = EUR_df['change'].sum()
    strength_df.iloc[1]= ['EUR', strength_EUR]
    
    JPY_df = Calculate_Abs_Strength(sym_jpy, sym_JPY_rev, cs_d1_0, cs_d1_1, prefix)
    strength_JPY = JPY_df['change'].sum()
    strength_df.iloc[2]= ['JPY', strength_JPY]
            
    GBP_df = Calculate_Abs_Strength(sym_gbp, sym_GBP_rev, cs_d1_0, cs_d1_1, prefix)
    strength_GBP = GBP_df['change'].sum()
    strength_df.iloc[3]= ['GBP', strength_GBP]
    
    AUD_df = Calculate_Abs_Strength(sym_aud, sym_AUD_rev, cs_d1_0, cs_d1_1, prefix)
    strength_AUD = AUD_df['change'].sum()
    strength_df.iloc[4]= ['AUD', strength_AUD]
    
    NZD_df = Calculate_Abs_Strength(sym_nzd, sym_NZD_rev, cs_d1_0, cs_d1_1, prefix)
    strength_NZD = NZD_df['change'].sum()
    strength_df.iloc[5]= ['NZD', strength_NZD]
    
    CAD_df = Calculate_Abs_Strength(sym_cad, sym_CAD_rev, cs_d1_0, cs_d1_1, prefix)
    strength_CAD = CAD_df['change'].sum()
    strength_df.iloc[6]= ['CAD', strength_CAD]
    
    CHF_df = Calculate_Abs_Strength(sym_chf, sym_CHF_rev, cs_d1_0, cs_d1_1, prefix)
    strength_CHF = CHF_df['change'].sum()
    strength_df.iloc[7]= ['CHF', strength_CHF]
    
    return strength_df

def Add_Prefix(symbols, prefix):
    for s in range(len(symbols)):
        symbols[s] = symbols[s] + prefix 
    
    return symbols

#to get Daily and H1 Strength
def get_abs_strength():
        
    abs_d1 = Get_Strength_Index(tf.Daily, 2)
    abs_h1 = Get_Strength_Index(tf.H1, 2)
    
    sort_d1 = abs_d1.sort_values('ABS_strength', axis=0, ascending=False)
    sort_h1 = abs_h1.sort_values('ABS_strength', axis=0, ascending=False)
    
    return sort_d1, sort_h1

#ti get series of abs strength    
def get_timeSeries_strength(timeframe, shift):
    
    abs = []
    
    for i in range(shift):
        abs.append(0)
        
    for i in range(len(abs)):
        abs[i] = Get_Strength_Index(timeframe, i)
        abs[i].rename(columns={'ABS_strength': i },inplace = True)
    
    abs_final = pd.DataFrame
    abs_final = abs[len(abs)-1]
    for i in range(len(abs)):
        abs_final = abs_final.merge(abs[len(abs)-2-i])
    
    return abs_final
    
#################################### MAIN #####################################
tf = timeframe()

prefix ='.lmx'
magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_add_2 = '127.0.0.200'
ip_1 = 'tcp://'+ ip_add_1
ip_2 = 'tcp://'+ ip_add_2

broker1 = broker(ip_1, magic_number)
broker2 = broker(ip_2, magic_number)

broker1.get_acct_info()
print(broker1.company)

timeframe = tf.Daily
shift = 6

abs_strength = Get_Strength_Index(timeframe, shift)
sort = abs_strength.sort_values('ABS_strength', axis=0, ascending=False)

print('\nshift = ', shift , '\ntimeframe = ', timeframe)
print(sort)


st_timeseries = get_timeSeries_strength(tf.Daily, 21)
print(st_timeseries)

d1, h1 = get_abs_strength()
print('\nDaily\n',d1,'\nHourly\n', h1)

#plot a bar chart
width = 0.8
x_axis=np.arange(len(d1))
fig, ax1 = plt.subplots()
ax1.bar(x_axis, d1['ABS_strength'], width, color = 'red')
plt.xticks(x_axis,d1['Currency'])
ax1.set_xlabel('currency')
ax1.set_ylabel('% Change')
ax1.set_title('Daily Absolute Strength Index')
ax1.axhline(2,0, ls='--', color='k' )
ax1.axhline(-2.0, ls='--', color='k' )
plt.show()

x_axis=np.arange(len(h1))
fig, ax1 = plt.subplots()
ax1.bar(x_axis, h1['ABS_strength'], width, color = 'blue')
plt.xticks(x_axis,h1['Currency'])
ax1.set_xlabel('currency')
ax1.set_ylabel('% Change')
ax1.set_title('H1 Absolute Strength Index')

ax1.axhline(0.5, ls='--', color='k' )
ax1.axhline(-0.5, ls='--', color='k' )
plt.show()

plt.subplot(121)
plt.bar(x_axis, d1['ABS_strength'], width, color = 'red')
plt.xticks(x_axis,d1['Currency'])
plt.xlabel('currency')
plt.ylabel('% Change')
plt.hlines(2.0,0,len(d1), linestyles='--', color='k' )
plt.hlines(-2.0,0,len(d1), linestyles='--', color='k' )
plt.title('Daily Absolute Strength Index')

plt.subplot(122)
plt.bar(x_axis, h1['ABS_strength'], width, color = 'blue')
plt.xticks(x_axis,h1['Currency'])
plt.xlabel('currency')
plt.ylabel('% Change')
plt.hlines(0.5,0,len(h1), linestyles='--', color='k' )
plt.hlines(-0.5,0,len(h1), linestyles='--', color='k' )
plt.title('Hourly Absolute Strength Index')

plt.show()