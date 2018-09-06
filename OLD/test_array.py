class sig:
    none = 99
    buy = 0
    sell = 1

trade_pair = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCHF','USDCAD', \
                       'EURJPY', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CHFJPY','CADJPY',\
                       'EURGBP', 'GBPAUD', 'GBPNZD', 'GBPCHF', 'GBPCAD', \
                       'EURAUD', 'EURNZD', 'EURCHF', 'EURCAD', \
                       'AUDCHF', 'AUDCAD', 'CADCHF', \
                       'NZDCHF', 'NZDCAD','AUDNZD']  
        
sig_detect = [] 
        
for symbol in trade_pair:
    signal = sig.buy
    
    if signal != sig.none:
        sig_detect.append([symbol, signal])
        
#print(sig_detect)
#print(len(sig_detect))
print(sig_detect[0][0])
print(sig_detect[0][1])

#print(sig.sell)