class ohlc:
    open = 0.0
    high = 1.2
    low = 3.3
    close = 4.4
    
test = ohlc()

print(test.open, test.high)

symbols=['EURUSD','GBPUSD','AUDUSD']

candle = []

for i in range(len(symbols)):
            candle.append(0.0)
            
#for i in range(len(symbols)):
#            candle[i] = ohlc()
#            
            
print(candle[0].open, candle[3].close)