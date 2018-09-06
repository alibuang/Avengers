import zmq
from time import sleep
from datetime import datetime

class broker_class:
    
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
           # msg = socket.recv_string()
    
        except zmq.Again as e:
            print ("1.Waiting for PUSH from MetaTrader 4.. :", e)
            sleep(1)
    
    # Function to retrieve data from ZeroMQ MT4 EA
    def remote_pull(self, socket):
    
        msg = None
        try:
            msg = socket.recv_string()
        #    msg = socket.recv()
        # msg = socket.recv(flags=zmq.NOBLOCK)
    
        except zmq.Again as e:
            print ("2.Waiting for PUSH from MetaTrader 4.. :", e)
            sleep(3)
    
        return msg
    
    def get_acct_info(self):

        acct_info = 'ACCTINFO'
        # print 'Check account info'
        self.remote_send(self.req_socket, acct_info)
        msg = self.remote_pull(self.pull_socket)
        print (msg)
        #msg = str(msg.decode("utf-8") )
        
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
    
    
magic_number = 123456
ip_add_1 = '127.0.0.100'
ip_add_2 = '127.0.0.200'
ip_1 = 'tcp://'+ ip_add_1
ip_2 = 'tcp://'+ ip_add_2


broker1 = broker_class(ip_1, magic_number)

broker1.get_acct_info()
print(broker1.company)

broker2 = broker_class(ip_2, magic_number)

broker2.get_acct_info()
print(broker2.company)