import sqlite3
import datetime
import csv

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return None

def create_table(conn):
    
    sql_tbl1 = '''
             CREATE TABLE IF NOT EXISTS Timeframe (
             timeframe_id integer PRIMARY KEY,
             timeframe_nm text,
             date_id integer,
             FOREIGN KEY (date_id) REFERENCES attribute (date_id)
             )'''

    sql_tbl2 = '''
             CREATE TABLE IF NOT EXISTS Date (
             date_id integer PRIMARY KEY,
             date_utc real,
             date_my real,
             symbols_id integer,
             FOREIGN KEY (symbols_id) REFERENCES attribute (symbols_id)
             )'''

    sql_tbl3 = '''
             CREATE TABLE IF NOT EXISTS Symbols (
             symbols_id integer PRIMARY KEY,
             symbols_nm text,
             price_id integer,
             FOREIGN KEY (price_id) REFERENCES attribute (price_id)
            )'''

    sql_tbl4 = '''
            CREATE TABLE IF NOT EXISTS Price (
            price_id integer PRIMARY KEY,
            open real,
            high real,
            low real,
            close real
            )'''

    cur = conn.cursor()
    cur.execute(sql_tbl1)
    cur.execute(sql_tbl2)
    cur.execute(sql_tbl3)
    cur.execute(sql_tbl4)

def check_brokerId(conn, broker_nm):

    cur = conn.cursor()
    cur.execute('select broker_id from broker where broker_nm  = ?',(broker_nm,))
    ret_id = cur.fetchone()
    # print 'broker id is :', ret_id

    if ret_id is None:
        return None
    else:
        return ret_id[0]


        
#    if id_check=='timeframe':
#        cur.execute('select timeframe_id from Timeframe where timeframe_nm  = ?',(content,))
#    elif id_check=='date':
#        cur.execute('select date_id from Timeframe where timeframe_nm  = ?',(content,))
    
    ret_id = cur.fetchone()
    # print 'broker id is :', ret_id

    if ret_id is None:
        return None
    else:
        return ret_id[0]

def check_attribId(conn, symbol):

    cur = conn.cursor()
    cur.execute('select attrib_id from attribute where symbol  = ?',(symbol,))
    ret_id = cur.fetchone()
    # print 'symbol id is :' ,ret_id

    if ret_id is None:
        return None
    else:
        return ret_id[0]

def insert_price(conn, priceData):

    sql = ''' INSERT OR IGNORE INTO price( attrib_id, broker_id, timestamp, bid, ask)
              VALUES(?,?,julianday(?),?,?) '''
    cur = conn.cursor()
    cur.execute(sql, priceData)
    return cur.lastrowid


def insert_broker(conn, brokerData):

    sql = ''' INSERT OR IGNORE INTO broker( broker_nm)
              VALUES(?) '''
    cur = conn.cursor()

    cur.execute(sql, brokerData)
    return cur.lastrowid

def check_id(conn, table, data):
    
    cur = conn.cursor()
    
    if table == 'timeframe':
        sql = 'select timeframe_id from Timeframe where timeframe_nm  = ?'
    elif table == 'date':
        sql = 'select date_id from Date where date_utc  = ?'
        
#    print(sql, '\n', data)    
    cur.execute(sql, data)
    
    ret_id = cur.fetchone()
    
    if ret_id is None:
        return None
    else:
        return ret_id[0]
    
    

def Insert_Data(conn, table, data):
    
#    print('data is ', data)
    cur = conn.cursor()
    
    if table == 'timeframe':
        sql = 'INSERT OR IGNORE INTO Timeframe ( timeframe_nm) VALUES(?)'
    elif table == 'date':
        sql = 'INSERT OR IGNORE INTO Date ( date_utc, date_my) VALUES(?,?)'
        
    cur.execute(sql, data)

#    cur.execute(sql, brokerData)
    return cur.lastrowid


def insert_attribute(conn, attribData):
    sql = ''' INSERT OR IGNORE INTO attribute( symbol, digits)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, attribData)
    return cur.lastrowid

def display_Data(conn):

    sql = ''' select *, strftime("%Y-%m-%d %H:%M:%f",timestamp) from price
        inner join broker on price.broker_id = broker.broker_id
        inner join attribute on price.attrib_id = attribute.attrib_id '''

    cur = conn.cursor()
    cur.execute(sql)

    return cur.fetchall()


#def save2db(database, dates, symbol, prices):
#    db.save2db(database, timeframe, datetimes, symbol, prices)
def save2db(database, timeframe, datetimes, symbol, prices):

    # create a database connection
    conn = create_connection(database)
    
    with conn:

        create_table(conn)        
        
#        check_id(conn, 'timeframe', 'M15')
        tf_data = (timeframe,)
        
        timeframe_id = check_id(conn, 'timeframe', tf_data)
        if timeframe_id is None:           
            timeframe_id = Insert_Data(conn, 'timeframe', tf_data)
            
#        date_id = check_id(conn, 'date', datetimes[0])
#        if date_id is None:
#            dateData = (datetimes[0], datetimes[1])
#            date_id = Insert_Data(conn, dateDatast')
#            
#        symbol_id = check_id(conn, symbol)
#        if symbol_id is None:
#            symbolData = (symbol,)
#            symbol_id = Insert_Data(conn, symbolData, 'Date')
#
#        priceData =(timeframe_id, date_id, symbol_id, prices[0], prices[1], prices[2], prices[3])
#        Insert_Data(conn, priceData)

        conn.commit()
        

def export2excel(database,filename):

    sql = '''
        select price_id, date(timestamp),time(timestamp), broker_nm, symbol, digits, bid, ask
        from price
        inner join broker on price.broker_id = broker.broker_id
        inner join attribute on price.attrib_id = attribute.attrib_id
    '''

    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    csvWriter = csv.writer(open(filename, "w"))
    csvWriter.writerows(rows)


def exportCustom(database, csv_filename, sql):

    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    csvWriter = csv.writer(open(csv_filename, "w"))
    csvWriter.writerows(rows)

if __name__ == '__main__':

     #------------------------ write to database -------------
    db_dir = 'database'
    database = db_dir + '\\' + 'avengers.db'
    
    save2db(database, 'M15', '', 'EURUSD', [1.2, 1.3, 1.4, 1.5])
     

#     broker_nm = 'Tifia'
#     symbol = 'AUDUSD'
#     digits = 5
#     bid = 1.23556
#     ask = 1.23775
#
#     save2db(database, broker_nm, symbol, digits, bid, ask)
#
#     conn = create_connection(database)
#     query_data = display_Data(conn)
#     for q in range(len(query_data)):
#         print query_data[q]

# write2db.save2db('test123.db',broker1.tms, broker1.company, symbols1[x],broker1.digits[x],broker1.bid[x],broker1.ask[x])


