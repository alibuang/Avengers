import sqlite3
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
             timeframe_nm integer
             )'''

    sql_tbl2 = '''
             CREATE TABLE IF NOT EXISTS Date (
             date_id integer PRIMARY KEY,
             date_utc real,
             date_my real
             )'''

    sql_tbl3 = '''
             CREATE TABLE IF NOT EXISTS Symbol (
             symbols_id integer PRIMARY KEY,
             symbols_nm text
             )'''

    sql_tbl4 = '''
            CREATE TABLE IF NOT EXISTS Price (
            price_id integer PRIMARY KEY,
            open real,
            high real,
            low real,
            close real,
            timeframe_id integer,
            date_id integer,
            symbols_id integer,
            FOREIGN KEY (timeframe_id) REFERENCES Timeframe (timeframe_id),
            FOREIGN KEY (date_id) REFERENCES Date(date_id),
            FOREIGN KEY (symbols_id) REFERENCES Symbols (symbols_id)
            )'''

    cur = conn.cursor()
    cur.execute(sql_tbl1)
    cur.execute(sql_tbl2)
    cur.execute(sql_tbl3)
    cur.execute(sql_tbl4)



def check_id(conn, table, data):
    
    cur = conn.cursor()
    
    sql = ''
    
    if table == 'timeframe':
        sql = 'select timeframe_id from Timeframe where timeframe_nm  = ?'
    elif table == 'date':
        sql = 'select date_id from Date where date_utc  = ?'
    elif table == 'symbol':
        sql = 'select symbols_id from Symbol where symbols_nm  = ?'
        
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
    elif table == 'symbol':
        sql = 'INSERT OR IGNORE INTO Symbol ( symbols_nm) VALUES(?)'
    elif table == 'price':
        sql = 'INSERT OR IGNORE INTO Price ( timeframe_id, date_id, symbols_id, open, high, low, close) VALUES(?,?,?,?,?,?,?)'
        
    cur.execute(sql, data)

    return cur.lastrowid

def display_Data(conn):

    sql = ''' select *, strftime("%Y-%m-%d %H:%M:%f",timestamp) from price
        inner join broker on price.broker_id = broker.broker_id
        inner join attribute on price.attrib_id = attribute.attrib_id '''

    cur = conn.cursor()
    cur.execute(sql)

    return cur.fetchall()


def save2db(database, timeframe, datetimes, symbol, prices):

    # create a database connection
    conn = create_connection(database)
    
    with conn:

        create_table(conn)        
        
        tf_data = (timeframe,)
        
        timeframe_id = check_id(conn, 'timeframe', tf_data)
        if timeframe_id is None:           
            timeframe_id = Insert_Data(conn, 'timeframe', tf_data)
            
        symbolData = (symbol,)
        symbol_id = check_id(conn, 'symbol', symbolData)
        if symbol_id is None:
            symbol_id = Insert_Data(conn, 'symbol', symbolData)
                
        from datetime import datetime
        
        data = (datetime.isoformat(datetimes[0]),)
        date_id = check_id(conn, 'date', data)
        
        if date_id is None:
        
            dateData = (datetime.isoformat(datetimes[0]),datetime.isoformat(datetimes[1]))
            date_id = Insert_Data(conn,'date', dateData)
                
            priceData =(timeframe_id, date_id, symbol_id, prices[0], prices[1], prices[2], prices[3])
            Insert_Data(conn, 'price', priceData)

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
    
    save2db(database, 15, ['2018-08-08','2018-08-25'], 'USDJPY', [1.2, 1.3, 1.4, 1.5])
     