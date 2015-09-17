import sqlite3
from configobj import ConfigObj

config = ConfigObj('config.ini')
dbfile=config['sqlite']['dbfile']
print dbfile


table1 = 'invoices'
table1_schema = '''
(TxnID  TEXT PRIMARY KEY NOT NULL,
TxnNumber TEXT,
CustomerRef_ListID    TEXT,
CustomerRef_FullName  TEXT,
TxnDate   DATE,
RefNumber TEXT,
Subtotal  REAL,
BalanceRemaining REAL,
IsPaid BOOLEAN,
json TEXT);
'''

sql = 'create table if not exists ' + table1 + table1_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)


# trouble with ListID not being unique track that down
table2 = 'customers'
table2_schema = '''
(FullName  TEXT PRIMARY KEY NOT NULL,
ListID TEXT,
Name TEXT,
CustomerType TEXT,
json TEXT);
'''

sql = 'create table if not exists ' + table2 + table2_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)
