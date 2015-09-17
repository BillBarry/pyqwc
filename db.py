import sqlite3
import xmltodict
import json
import sqlite3
from configobj import ConfigObj

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

config = ConfigObj('config.ini')
dbfile=config['sqlite']['dbfile']

def insert_invoice(responseXML):
    insertsql = "INSERT INTO invoices (TxnID,TxnNumber,CustomerRef_ListID,CustomerRef_FullName,TxnDate,RefNumber,Subtotal,BalanceRemaining,IsPaid) VALUES (?, ?, ?,?,?,?,?,?,?)"
    #ith sqlite3.connect(dbfile) as conn:
    with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:            
        doc = xmltodict.parse(responseXML)
        inv = doc["QBXML"]["QBXMLMsgsRs"]["InvoiceQueryRs"]["InvoiceRet"]
        if type(inv) is list:
            for i in inv:
                CustomerRef_ListID = i['CustomerRef']['ListID']
                CustomerRef_FullName = i['CustomerRef']['FullName']
                conn.execute(insertsql, (i["TxnID"],i["TxnNumber"],CustomerRef_ListID,CustomerRef_FullName,i["TxnDate"],i["RefNumber"],float(i["Subtotal"]),float(i["BalanceRemaining"]),i["IsPaid"]))
        else:
            i = inv
            CustomerRef_ListID = i['CustomerRef']['ListID']
            CustomerRef_FullName = i['CustomerRef']['FullName']
            conn.execute(insertsql, (i["TxnID"],i["TxnNumber"],CustomerRef_ListID,CustomerRef_FullName,i["TxnDate"],i["RefNumber"],float(i["Subtotal"]),float(i["BalanceRemaining"]),i["IsPaid"]))

def insert_customer(responseXML):
    insertsql = "INSERT INTO customers (ListID,Name,FullName,CustomerType)VALUES (?, ?, ?, ?)"
    with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:            
        doc = xmltodict.parse(responseXML)
        inv = doc["QBXML"]["QBXMLMsgsRs"]["CustomerQueryRs"]["CustomerRet"]
        if type(inv) is list:
            for i in inv:
                if "CustomerTypeRef" in i:
                    CustomerType = i["CustomerTypeRef"]["FullName"]
                else:
                    CustomerType = ""
                try:
                    conn.execute(insertsql, (i["ListID"],i["Name"],i['FullName'],CustomerType))
                except:
                    #print "DB not unique",i["ListID"],i["FullName"]
                    pass
        else:
            i = inv
            CustomerType = i["CustomerTypeRef"]["FullName"]
            conn.execute(insertsql, (i["ListID"],i["Name"],i['FullName'],CustomerType))

            
