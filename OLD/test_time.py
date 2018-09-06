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
    
def Add_Prefix(symbols, prefix):
    for s in range(len(symbols)):
        symbols[s] = symbols[s] + prefix 
    
    return symbols
    
tf = timeframe()
timeframe = tf.Daily
shift = 1
prefix ='.lmx'
magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_add_2 = '127.0.0.200'
ip_1 = 'tcp://'+ ip_add_1
ip_2 = 'tcp://'+ ip_add_2

broker1 = broker(ip_1, magic_number)
broker2 = broker(ip_2, magic_number)

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