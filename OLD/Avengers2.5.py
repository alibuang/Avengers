import pandas as pd
import numpy as np
from mt4zmq import broker_class as bk
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import telegram
from datetime import datetime
from time import sleep
from ffcalnews import chk_news

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
    
class sig:
    none = 99
    buy = 0
    sell = 1
    
ea_name = 'Avengers2.5' 
    
LOTS = 0.01
SLIP = 30
STOP_LOSS = 100
TAKE_PROFIT = 100
COMMENTS = ea_name
SPREAD_LIMIT = 30

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
#                print('Symbol Not Found')
                Log('calculate_abs_strength, symbol not found')
        
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
    
    sym_usd = ['EURUSD','GBPUSD','AUDUSD','NZDUSD','USDJPY','USDCHF','USDCAD']
    sym_USD_rev=['EURUSD','AUDUSD','GBPUSD','NZDUSD']
    
    sym_eur = ['EURUSD', 'EURGBP', 'EURAUD', 'EURNZD', 'EURJPY','EURCHF','EURCAD']
    sym_EUR_rev = []
    
    sym_jpy = ['USDJPY', 'GBPJPY', 'EURJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY', 'CADJPY']
    sym_JPY_rev = ['USDJPY', 'GBPJPY', 'EURJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY', 'CADJPY']
    
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
    
    cs_d1_0 = broker1.get_OHLC(Symbols, timeframe , shift)
    cs_d1_1 = broker1.get_OHLC(Symbols, timeframe , shift + 1)
    
    datetime = cs_d1_0[0].timestamp
    
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
    
    return strength_df, datetime

def Add_Prefix(symbols, prefix):
    for s in range(len(symbols)):
        symbols[s] = symbols[s] + prefix 
    
    return symbols

#to get Daily and H1 Strength
def get_abs_strength(sft_D1, sft_H1):
        
    abs_d1, dt_d1 = Get_Strength_Index(tf.Daily, sft_D1)
    abs_h1, dt_h1 = Get_Strength_Index(tf.H1, sft_H1)
    
    sort_d1 = abs_d1.sort_values('ABS_strength', axis=0, ascending=False)
    sort_h1 = abs_h1.sort_values('ABS_strength', axis=0, ascending=False)
    
    return sort_d1, sort_h1, dt_d1, dt_h1

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

def plot_Chart(d1, h1, date, time):
    
    daily_threshold = 2.0
    hourly_threshold = 1.0
    
    x_axis=np.arange(len(h1))
    width = 0.8
    font_ax = FontProperties()
    font_ax.set_size('xx-small')
    
    font_lbl = FontProperties()
    font_lbl.set_size('small')
    font_lbl.set_style('italic')
    
    font_ttl = FontProperties()
    font_ttl.set_size('small')
#    font_ttl.set_weight('bold')
   
        
    plt.subplot(121)
    plt.bar(x_axis, d1['ABS_strength'], width, color = 'red')
    plt.xticks(x_axis,d1['Currency'], fontproperties=font_ax, rotation=90)
    plt.xlabel('currency', fontproperties= font_lbl )
    plt.ylabel('% Change', fontproperties= font_lbl)
    plt.hlines(daily_threshold,0,len(d1), linestyles='--', color='k' )
    plt.hlines(-daily_threshold,0,len(d1), linestyles='--', color='k' )
    plt.title('Daily Absolute Strength\n ' + str(date), fontproperties= font_ttl)
     
    plt.subplot(122)
    plt.bar(x_axis, h1['ABS_strength'], width, color = 'blue')
    plt.xticks(x_axis,h1['Currency'],fontproperties=font_ax, rotation=90)
    plt.xlabel('currency', fontproperties= font_lbl)
    plt.hlines(hourly_threshold,0,len(h1), linestyles='--', color='k' )
    plt.hlines(-hourly_threshold,0,len(h1), linestyles='--', color='k' )
    plt.title('Hourly Absolute Strength\n' + str(time), fontproperties= font_ttl)
    
    plt.savefig('index.png')
    plt.clf()
#    plt.show()
    
############################ To detect signal #################################
def Analyze_Signal(symbol, d1, h1):
#    trade_pair = ['EURUSD','GBPUSD','USDJPY','EURJPY']
    daily_high_thres = 2
    daily_low_thres = 0.25
    hourly_high_thres = 1
    hourly_low_thres = 0.25
       
    #get currency
    base_currency = symbol[:3]
    quote_currency = symbol[3:]
    
#    print('\n', base_currency, quote_currency)
    
    #get base and quote strength for trend (Daily)
    base_sgth_d1 = d1[d1['Currency'] == base_currency].iloc[0,1]
    quote_sgth_d1 = d1[d1['Currency'] == quote_currency].iloc[0,1]
    
    #get base and quote strength for entry (H1)
    base_sgth_h1 = h1[h1['Currency'] == base_currency].iloc[0,1]
    quote_sgth_h1 = h1[h1['Currency'] == quote_currency].iloc[0,1]
    
# Base Currency factor    
    # Check for trend --- Daily
    
    signal = sig.none

    if base_sgth_d1 > daily_high_thres and quote_sgth_d1 < daily_low_thres :
        if base_sgth_h1 > hourly_high_thres and quote_sgth_h1 < hourly_low_thres :
            signal = sig.buy
#            print(symbol, 'Base='+str(base_sgth_h1), 'Quote='+str(quote_sgth_h1))
            
    elif base_sgth_d1 < -daily_high_thres and quote_sgth_d1 > -daily_low_thres :
        if base_sgth_h1 < -hourly_high_thres and quote_sgth_h1 > -hourly_low_thres :
            signal = sig.sell
#            print(symbol, 'Base='+str(base_sgth_h1), 'Quote='+str(quote_sgth_h1))
        
# Quote currency factor
    #trend Daily
    elif quote_sgth_d1 < -daily_high_thres and base_sgth_d1 > -daily_low_thres :
        if quote_sgth_h1 < -hourly_high_thres and base_sgth_h1 > -hourly_low_thres :
            signal = sig.buy
#            print(symbol, 'Base='+str(base_sgth_h1), 'Quote='+str(quote_sgth_h1))
        
    elif quote_sgth_d1 > daily_high_thres  and base_sgth_d1 < daily_low_thres :
        if quote_sgth_h1 > hourly_high_thres and base_sgth_h1 < hourly_low_thres :
            signal = sig.sell
#            print(symbol, 'Base='+str(base_sgth_h1), 'Quote='+str(quote_sgth_h1))
    
    return signal

def get_CS_Today():
    
    symbol = ['EURUSD']
    symbol = Add_Prefix(symbol, prefix)
    
    tm = timeframe.Daily
    shift = 0
    
    daily_data = broker1.get_OHLC(symbol, tm , shift)
    today_candle = daily_data[0].timestamp
    
    return today_candle

def get_CS_Hour():
    
    symbol = ['EURUSD']
    symbol = Add_Prefix(symbol, prefix)
    
    tm = timeframe.H1
    shift = 0
    
    daily_data = broker1.get_OHLC(symbol, tm , shift)
    now_h1_candle = daily_data[0].timestamp
    
    return now_h1_candle

def Get_Signal(trade_pair):
    
    #get strength index for daily and h1    
    today = get_CS_Today().weekday()
    print('today CS day', today)
    
    if today == 0:
        d1_shift = 2
    elif today in [5,6]:
        d1_shift = 0
    else:
        d1_shift = 1
        
#    print('today=',today)
    
    d1, h1, dt_d1, dt_h1 = get_abs_strength(d1_shift, 1)
    print('CandleStick being Analyzed', '\nDate:',dt_d1,'\nTime:',dt_h1)
    print('\nDaily\n',d1,'\nHourly\n',h1,'\n')
    
    txt = 'CandleStick being Analyzed'+'\nDate:'+str(dt_d1)+'\nTime:'+str(dt_h1)
    Log(txt)
    txt = '\nDaily\n' + str(d1) +'\nHourly\n' + str(h1) 
    Log(txt)
    
    #plot strength chart or save into file .png
    date = dt_d1.date()
    time = dt_h1.time()
        
    plot_Chart(d1, h1, date, time)
    
    #analyze and get signal
    sig_detect = [] 
    
    for symbol in trade_pair:
        signal = Analyze_Signal(symbol, d1, h1)
        
        if signal != sig.none:
            sig_symbol = symbol + prefix
            sig_detect.append([sig_symbol, signal])
              
    print('\nSignal detected\n',sig_detect)        
    txt = 'Signal detected :' + str(sig_detect)
    Log(txt)
    
    return sig_detect
            
    
def Auto_Trade(sig_detect):
    
    #check for open position for pair with open signal
    symbols_det=[]
    for i in range(len(sig_detect)):
        symbols_det.append(sig_detect[i][0])

    broker1.get_count(symbols_det) #get trade count
    broker1.get_price(symbols_det) #get price and spread
    
    
    #if signal is detected , send order to MT4
    for i in range(len(sig_detect)):
        
        #if there is no open position then can trade
        if broker1.trade_count[i] == 0 and broker1.spread[i] < SPREAD_LIMIT:
        
            #assign symbol and order type
            symbol = sig_detect[i][0]
            order_type = sig_detect[i][1]
            
            #assign open price
            if order_type == sig.buy:
                price = broker1.ask[i]
            elif order_type == sig.sell:
                price = broker1.bid[i]
                
            #send order to MT4
            lot = LOTS
            slip = SLIP
            stop_loss = STOP_LOSS
            take_profit = TAKE_PROFIT
            comments = COMMENTS
            
            broker1.send_order(order_type, symbol, price, lot, slip, stop_loss, \
                              take_profit, comments)
            
            #send telegram message
            order = None
            if order_type == sig.buy:
                order = 'BUY'
            elif order_type == sig.sell:
                order = 'SELL'
            
            timestamp = str(datetime.now().replace(microsecond=0))
             
            text_msg = timestamp + '\n' + symbol + ': ' +order + ' order was sent'
            bot.send_message(chat_id=chat_id, text=text_msg)
            
        else:
            
            timestamp = str(datetime.now().replace(microsecond=0))
            print(timestamp, sig_detect[i][0], 'NO trade due to open position \
            exits OR spread above limit. open_position=', broker1.trade_count[i],\
            ', spread=', broker1.spread[i] )
            
            txt = sig_detect[i][0] + '|NO trade due to open position \
            exits OR spread above limit. open_position=' + str(broker1.trade_count[i]) + \
            ', spread='+ str(broker1.spread[i])
            Log(txt)
        
    # send strength index chart to telegram
    timestamp = str(datetime.now().replace(microsecond=0))
    bot.send_photo(chat_id=chat_id, photo=open('index.png','rb'), \
                   caption='absolute strength index\n'+timestamp)


def check_candle(symbols, tf, shift):
    
    h1_ohlc = broker1.get_OHLC(symbols, tf ,shift)
    
    candle_good = False
    
    for i in np.arange(0,len(symbols)-1): 
        if h1_ohlc[i].timestamp == h1_ohlc[i+1].timestamp:
            candle_good = True        
#            print(i, 'candle good status:', candle_good, h1_ohlc[i].symbol, h1_ohlc[i].timestamp)
#            
#            txt = str(i) + 'candle good status:' + str(candle_good) + h1_ohlc[i].symbol + str(h1_ohlc[i].timestamp)
#            Log(txt)
            
        else:
            candle_good = False
#            print(i, 'candle good status:', candle_good, h1_ohlc[i].symbol, h1_ohlc[i].timestamp)
#            
#            txt = str(i) + 'candle good status:' + str(candle_good) + h1_ohlc[i].symbol + str(h1_ohlc[i].timestamp)
#            Log(txt)
            
            break;
        
    return candle_good

def Log(txt):
    
    file = open('avenger.log','a')
    file.write('\n')
    
    header = str(datetime.now().replace(microsecond=0)) + '|'
    file.write(header)
    file.write(txt)
    file.close()

#################################### MAIN #####################################

token='488376978:AAFvFovR-Zin9VXR-AhCs0RRXXP149s_rdk'
bot = telegram.Bot(token= token)
chat_id=-1001142683257

tf = timeframe()

prefix ='.lmx'
magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_add_2 = '127.0.0.200'
ip_1 = 'tcp://'+ ip_add_1
ip_2 = 'tcp://'+ ip_add_2

broker1 = bk(ip_1, magic_number)
broker2 = bk(ip_2, magic_number)


broker1.get_acct_info()
print(broker1.company)
txt= broker1.company
Log(txt)

prev_time = None
curr_time = None

Symbols = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCHF','USDCAD', \
                   'EURJPY', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY','CADJPY',\
                   'EURGBP', 'GBPAUD', 'GBPNZD', 'GBPCHF', 'GBPCAD', \
                   'EURAUD', 'EURNZD', 'EURCHF', 'EURCAD', \
                   'AUDCHF', 'AUDCAD', 'CADCHF', \
                   'NZDCHF', 'NZDCAD','AUDNZD']  
Symbols = Add_Prefix(Symbols, prefix)

Trade_Pair = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCHF','USDCAD', \
                   'EURJPY', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY','CADJPY',\
                   'EURGBP', 'GBPAUD', 'GBPNZD', 'GBPCHF', 'GBPCAD', \
                   'EURAUD', 'EURNZD', 'EURCHF', 'EURCAD', \
                   'AUDCHF', 'AUDCAD', 'CADCHF', \
                   'NZDCHF', 'NZDCAD','AUDNZD']  

#################################################################

#print('The End')
#import sys
#sys.exit()
##################################################################

while True:    
    try:
        
        curr_time = get_CS_Hour().hour
        minute = datetime.now().minute
        
        while curr_time != prev_time and minute > 3 :
            
                 
            d1_candle_status = check_candle(Symbols, timeframe.H1, 1)  
            h1_candle_status = check_candle(Symbols, timeframe.M15, 1)  
            print('M15 status:', h1_candle_status, '\nHourly CS status:', d1_candle_status)
            
            txt= 'M15 status:' + str(h1_candle_status) + '\nHourly CS status:' \
            + str(d1_candle_status)
            Log(txt)
            
            if h1_candle_status and d1_candle_status:
                            
                signals = Get_Signal(Trade_Pair)
#                Auto_Trade(signals)
                
                # send strength index chart to telegram
                timestamp = str(datetime.now().replace(microsecond=0))
                bot.send_photo(chat_id=chat_id, photo=open('index.png','rb'), \
                caption='absolute strength index\n'+timestamp, timeout=50)
            
                chk_news()
                
                prev_time = curr_time
                print('current h1 CS is ',str(prev_time))    
                   
        sleep(60) #sleep for 1 minit
        
    except Exception as err:
        
        print(err,"\nretrying due to error ...")
        txt= str(err) + 'retrying due to error ...'
        Log(txt)
        
        sleep(10)
        continue
    