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
             CREATE TABLE IF NOT EXISTS price (
             price_id integer PRIMARY KEY,
             bid real,
             ask real,
             timestamp real,
             attrib_id integer,
             broker_id integer,
             FOREIGN KEY (attrib_id) REFERENCES attribute (attrib_id),
             FOREIGN KEY (broker_id) REFERENCES broker (broker_id)
             )'''

    sql_tbl2 = '''
             CREATE TABLE IF NOT EXISTS broker (
             broker_id integer PRIMARY KEY,
             broker_nm text
            )'''

    sql_tbl3 = '''
            CREATE TABLE IF NOT EXISTS attribute (
            attrib_id integer PRIMARY KEY,
            symbol text,
            digits integer
            )'''

    cur = conn.cursor()
    cur.execute(sql_tbl1)
    cur.execute(sql_tbl2)
    cur.execute(sql_tbl3)

def check_brokerId(conn, broker_nm):

    cur = conn.cursor()
    cur.execute('select broker_id from broker where broker_nm  = ?',(broker_nm,))
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


def save2db(database,timestamp, broker_nm, symbol, digits, bid, ask):

    # create a database connection
    conn = create_connection(database)
    with conn:

        create_table(conn)

        broker_id = check_brokerId(conn,broker_nm)
        if broker_id is None:
            brokerData = (broker_nm,)
            broker_id = insert_broker(conn, brokerData)

        attrib_id = check_attribId(conn,symbol)
        if attrib_id is None:
            attribData = (symbol,digits)
            attrib_id = insert_attribute(conn,attribData)

        priceData =(attrib_id, broker_id, timestamp,bid,ask)
        insert_price(conn, priceData)

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

# if __name__ == '__main__':
#
#     database = 'superipin.db'
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


