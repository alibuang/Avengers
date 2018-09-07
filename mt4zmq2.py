import zmq
from time import sleep
from datetime import datetime

minLOT = 0.01
RISK = 'HIGH'
LOTS = 0.01
lot2usd_ratio = 10

class ohlc:
    open = 0.0
    high = 0.0
    low = 0.0
    close = 0.0
    symbol = ''
    timestamp = None
    
    

class broker_class:
    tms = None
    trade_count = None
    err_msg = None
    req_socket = None
    pull_socket = None
    symbol = None
    magic_number = None
    
#    class ohlc:
#        open = 0.0
#        high = 0.0
#        low = 0.0
#        close = 0.0
#    
    
   
    def __init__(self, broker, magic_no):
        # def __init__(self, broker, pair, magic_no):
        self.get_socket(broker)
        # self.symbol = pair
        self.magic_number = magic_no

    def get_socket(self, broker):
        context = zmq.Context()

        socket_req = broker + ':5555'
        socket_pull = broker + ':5556'

        # Create REQ Socket
        reqSocket = context.socket(zmq.REQ)
        reqSocket.connect(socket_req)
        self.req_socket = reqSocket

        # Create PULL Socket
        pullSocket = context.socket(zmq.PULL)
        pullSocket.connect(socket_pull)
        self.pull_socket = pullSocket
        
    # Function to send commands to ZeroMQ MT4 EA
    def remote_send(self, socket, data):
    
        msg = None
        try:
    
            socket.send_string(data)
            msg = socket.recv_string()
    
        except zmq.Again as e:
            print ("1.Waiting for PUSH from MetaTrader 4.. :", e)
            sleep(1)
    
    # Function to retrieve data from ZeroMQ MT4 EA
    def remote_pull(self, socket):
    
        msg = None
        try:
            msg = socket.recv_string()
        # msg = socket.recv(flags=zmq.NOBLOCK)
    
        except zmq.Again as e:
            print ("2.Waiting for PUSH from MetaTrader 4.. :", e)
            sleep(3)
    
        return msg

    def get_price(self, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        # print sym
        get_rates = "RATES"+ sym
        # print get_rates

        self.remote_send(self.req_socket, get_rates)
        msg = self.remote_pull(self.pull_socket)

        self.bid = []
        self.ask = []
        self.spread = []
        self.digits = []
        self.avg_price = []
        for i in range(len(symbols)):
            self.bid.append(0.0)
            self.ask.append(0.0)
            self.spread.append(0.0)
            self.digits.append(0)
            self.avg_price.append(0.0)

        # print msg
        if msg is not None:
            quote = msg.split('|')
            self.tms =  datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')

            for i in range(len(symbols)):
                self.bid[i] = float(quote[(i*4)+1])
                self.ask[i] = float(quote[(i*4)+2])
                self.spread[i] = float(quote[(i*4)+3])
                self.digits[i] = int(float(quote[(i*4)+4]))
                self.avg_price[i] = round((self.bid[i] + self.ask[i])/2,self.digits[i])
            # print i

            # print self.bid, self.ask, self.avg_price

    def get_OHLC(self, symbols, timeframe, shift):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        # print sym
        get_rates = "OHLC"+ '|' + str(timeframe) + '|' +str(shift)  +sym 
        # print get_rates

        self.remote_send(self.req_socket, get_rates)
        msg = self.remote_pull(self.pull_socket)

        candle_price = []
        for i in range(len(symbols)):
            candle_price.append(0.0)
        
        for i in range(len(symbols)):
            candle_price[i]=ohlc()
        
        
#        print(msg)
        if msg is not None:
            quote = msg.split('|')
            tms =  datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')

            for i in range(len(symbols)):
                candle_price[i].open = float(quote[(i*4)+1])
                candle_price[i].high = float(quote[(i*4)+2])
                candle_price[i].low = float(quote[(i*4)+3])
                candle_price[i].close = float(quote[(i*4)+4])
                candle_price[i].symbol = symbols[i]
                candle_price[i].timestamp = tms
                
             
        return candle_price


    def get_count(self, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        self.trade_count =[]
        for a in range(len(symbols)):
            self.trade_count.append(0)

        req_count = "COUNT|"+ str(self.magic_number) + sym

        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        # msg = 'COUNT|1|2|3|4|5|6'
        # print msg

        if msg is not None:
            quote = msg.split('|')
            for i in range(len(symbols)):
                # print i, '\t', quote[i + 1]
                self.trade_count[i] = int(float(quote[i+1]))

            # print self.trade_count

    def get_count2(self, mag_num, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        self.trade_count =[]
        for a in range(len(symbols)):
            self.trade_count.append(0)

        req_count = "COUNT|"+ str(mag_num) + sym

        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        # msg = 'COUNT|1|2|3|4|5|6'
        # print msg

        if msg is not None:
            quote = msg.split('|')
            for i in range(len(symbols)):
                # print i, '\t', quote[i + 1]
                self.trade_count[i] = int(float(quote[i+1]))

            # print self.trade_count

    def get_openTime(self, symbol):

        lastOpenTime = None
        mt4ServerTime = None
        req_OpenTime = "LASTOPENTIME|" + str(self.magic_number) + "|" + symbol

        self.remote_send(self.req_socket, req_OpenTime)
        msg = self.remote_pull(self.pull_socket)

        if msg is not None:
            quote = msg.split('|')
            lastOpenTime = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')
            mt4ServerTime = datetime.strptime(quote[1], '%Y.%m.%d %H:%M:%S')

        return  lastOpenTime, mt4ServerTime

    #this function will return trade count, order type  and  last price
    def get_order_status(self, symbols):
        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        get_status = "STATUS|" + str(self.magic_number) + sym
        # print get_status

        self.remote_send(self.req_socket, get_status)
        msg = self.remote_pull(self.pull_socket)

        # print msg

        self.trade_count = []
        self.order_type = []
        self.last_price = []
        for i in range(len(symbols)):
            self.trade_count.append(0.0)
            self.order_type.append(None)
            self.last_price.append(0.0)

        # print msg
        if msg is not None:
            quote = msg.split('|')

            for i in range(len(symbols)):
                self.trade_count[i] = int(float(quote[(i * 3) + 0]))
                self.order_type[i] = int(float(quote[(i * 3) + 1]))
                self.last_price[i] = float(quote[(i * 3) + 2])

            # print self.trade_count, self.order_type, self.last_price

    #this function will return trade count, order type  and  last price
    def get_open_price(self, symbol):

        get_price = "OPENPRICE|" + str(self.magic_number) + symbol
        # print get_status

        self.remote_send(self.req_socket, get_price)
        msg = self.remote_pull(self.pull_socket)

        # print msg

        trade_count = 0
        order_type = None
        price = []

        # print msg
        if msg is not None:
            quote = msg.split('|')
            trade_count = int(float(quote[0]))
            order_type = quote[1]
            for i in range(trade_count):
                price.append(quote[1+i])

        return trade_count, order_type, price



    def get_profit(self, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        self.profit =[]
        for a in range(len(symbols)):
            self.profit.append(0.0)

        req_count = "PROFIT|"+ str(self.magic_number) + sym

        print (req_count)
        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        print (msg)

        if msg is not None:
            quote = msg.split('|')
            for i in range(len(symbols)):
                # print i, '\t', quote[i + 1]
                self.profit[i] = int(float(quote[i+1]))

        print (self.profit)
        
    def get_profit_by_Magic_Num(self, magic_number):

#        self.profit =[]

        req_count = "PROFIT_MAGIC|"+ str(magic_number)

#        print (req_count)
        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        print (req_count, msg)

        profit = 0
        if msg is not None:
            quote = msg.split('|')
            header = quote[0]
            if len(quote) > 1:
                profit = float(quote[1])
        
#        print(quote)    
        return profit



    def send_order(self, order_type, symbol, price, lot=0.01, slip=10, \
                   stop_loss=0, take_profit=0, comments="no comments"):

        #format 'TRADE|OPEN|ordertype|symbol|openprice|lot|SL|TP|Slip|comments|magicnumber'

        order = "TRADE|OPEN|"+ str(order_type)+"|" + symbol +"|"+ str(price)+ \
        "|"+ str(lot)+ "|" + str(stop_loss)+ "|"+ str(take_profit) +"|" + \
        str(slip)+"|"+comments +"|"+str(self.magic_number)
        print (order)

        self.remote_send(self.req_socket, order)
    # msg = remote_pull(self.pull_socket)
    
    def send_order2(self, mag_num, order_type, symbol, price, lot=0.01, slip=10, \
                   stop_loss=0, take_profit=0, comments="no comments"):

        #format 'TRADE|OPEN|ordertype|symbol|openprice|lot|SL|TP|Slip|comments|magicnumber'

        order = "TRADE|OPEN|"+ str(order_type)+"|" + symbol +"|"+ str(price)+ \
        "|"+ str(lot)+ "|" + str(stop_loss)+ "|"+ str(take_profit) +"|" + \
        str(slip)+"|"+comments +"|"+str(mag_num)
        print (order)

        self.remote_send(self.req_socket, order)
    # msg = remote_pull(self.pull_socket)

    def order_close_new(self, symbols):

        str_symb = ''
        # print symbols
        for s in symbols:
            str_symb = str_symb +'|' + s
        # print str_symb

        # format 'TRADE|CLOSE|magicnumber|symbol1, symbol2, ..'
        close_order = 'TRADE|CLOSE|'+ str(self.magic_number) + str_symb

        print (close_order)
        # sys.exit()

        self.remote_send(self.req_socket, close_order)

    def order_close_by_magicnumber(self, magic_number):

        # format 'TRADE|CLOSE|magicnumber|symbol1, symbol2, ..'
        close_order = 'CLOSE_MAGICNUM|'+ str(magic_number) 

        print(close_order)
        # sys.exit()

        self.remote_send(self.req_socket, close_order)
        

    def get_zmq_ver(self):

        chk_ver = 'EAVERSION'
        print ('Check ZMQ version')
        self.remote_send(self.req_socket, chk_ver)
        msg = self.remote_pull(self.pull_socket)

        self.zmq_mt4_ver = msg

    def get_acct_info(self):

        acct_info = 'ACCTINFO'
        # print 'Check account info'
        self.remote_send(self.req_socket, acct_info)
        msg = self.remote_pull(self.pull_socket)
        # print msg

        if msg is not None:
            quote = msg.split('|')
            self.company = quote[0]
            self.acctName = quote[1]
            self.acctNumber = int(float(quote[2]))
            self.balance = float(quote[3])
            self.profit = float(quote[4])

            if quote[5] == 'true' or quote[5] == 'True':
                self.connection = True
            else:
                self.connection = False

    def init_symbol(self, symbols):

        str_symb = ''
        for s in symbols:
            str_symb = str_symb + '|' + s

        init_symbols = 'INITIALIZE' + str_symb
        print ('Initialize MT4 Symbols ...')

        self.remote_send(self.req_socket, init_symbols)

    def get_lots(self):
        lots = 0.0

        #----------------------
        if minLOT == 0.01:
            rounders = 2
        elif minLOT == 0.1:
            rounders = 1
        else:
            rounders = 0

        #------------------------
        if RISK == 'HIGH':
            pipRisk = 200
        elif RISK == 'MEDIUM':
            pipRisk = 500
        elif RISK == 'LOW':
            pipRisk = 1000

        #----------------------------
        if RISK != 'manual':
            usdPerPip = self.balance / pipRisk
            lots = round((usdPerPip / lot2usd_ratio),rounders)
        elif RISK == 'manual':
            lots = LOTS

        return lots
    
    def get_opmagicnum(self):

        req_count = "MAGICNUM|"

        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        # msg = 'COUNT|1|2|3|4|5|6'
        print('return msg for magic number = ', msg)

        magic_numbers = []
        
        if msg is not None:
            quote = msg.split('|')
            header = quote[0]
            if len(quote) > 1:
                data = quote[1:]
            
                for d in data:
                    magic_numbers.append(int(d))
                
#
        return magic_numbers
