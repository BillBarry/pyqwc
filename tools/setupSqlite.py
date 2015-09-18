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
IsPaid BOOLEAN);
'''

sql = 'create table if not exists ' + table1 + table1_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)


# trouble with ListID not being unique track that down
table2 = 'customers'
table2_schema = '''
(ListID  TEXT PRIMARY KEY NOT NULL,
FullName TEXT,
Name TEXT,
CustomerType TEXT);
'''

sql = 'create table if not exists ' + table2 + table2_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)

table3 = 'invoice_line'
table3_schema = '''
(TxnLineID  TEXT PRIMARY KEY NOT NULL,
CustomerRef_FullName TEXT,
CustomerRef_ListID TEXT,
ItemRef_ListID TEXT,
ItemRef_FullName Text,
Quantity Text,
TxnDate Date);
'''

sql = 'create table if not exists ' + table3 + table3_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)

table4 = 'inventoryitems'
table4_schema = '''
(ListID  TEXT PRIMARY KEY NOT NULL,
Name TEXT,
FullName TEXT,
IsActive BOOLEAN,
SalesDesc TEXT,
SalesPrice REAL,
PurchaseCost REAL,
IncomeAccountRef_FullName TEXT,
AssetAccountRef_FullName TEXT,
QuantityOnHand INTEGER);
'''

sql = 'create table if not exists ' + table4 + table4_schema
with sqlite3.connect(dbfile) as conn:
    conn.execute(sql)



    
