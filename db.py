import sqlite3
import xmltodict
import json
import sqlite3
from configobj import ConfigObj

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

config = ConfigObj('config.ini')
dbfile=config['sqlite']['dbfile']

def insert_record(responseXML,querytype=""):
    if querytype == 'Invoice':
        insertsql = "INSERT INTO invoices (TxnID,TxnNumber,CustomerRef_ListID,CustomerRef_FullName,TxnDate,RefNumber,Subtotal,BalanceRemaining,IsPaid) VALUES (?, ?, ?,?,?,?,?,?,?)"
        itemsql = "INSERT INTO invoice_line (TxnLineID,CustomerRef_FullName,CustomerRef_ListID,ItemRef_ListID,ItemRef_FullName,Quantity,TxnDate) VALUES (?, ?, ?, ?, ?, ?, ?)"
        with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:            
            doc = xmltodict.parse(responseXML)
            inv = doc["QBXML"]["QBXMLMsgsRs"]["InvoiceQueryRs"]["InvoiceRet"]
            if type(inv) is list:
                for i in inv:
                    CustomerRef_ListID = i['CustomerRef']['ListID']
                    CustomerRef_FullName = i['CustomerRef']['FullName']
                    TxnDate = i['TxnDate']
                    try:
                        conn.execute(insertsql, (i["TxnID"],i["TxnNumber"],CustomerRef_ListID,CustomerRef_FullName,i["TxnDate"],i["RefNumber"],
                                                 float(i["Subtotal"]),float(i["BalanceRemaining"]),i["IsPaid"]))
                    except:
                        pass
                    if 'InvoiceLineRet' in i:
                        for L in i['InvoiceLineRet']:
                            for J in L:
                                if not (type(L) is unicode and type(J) is unicode):
                                    if J == 'TxnLineID':
                                        TxnLineID = L[J]
                                    elif J == 'ItemRef':
                                        ItemRef_ListID = L[J]['ListID']
                                        ItemRef_FullName = L[J]['FullName']
                                    elif J == 'Quantity':
                                        Quantity = L[J]
                            try:
                                conn.execute(itemsql, (TxnLineID,CustomerRef_FullName,CustomerRef_ListID,ItemRef_ListID,ItemRef_FullName,Quantity,TxnDate))
                            except:
                                pass
            else:
                i = inv
                CustomerRef_ListID = i['CustomerRef']['ListID']
                CustomerRef_FullName = i['CustomerRef']['FullName']
                try:
                    conn.execute(insertsql, (i["TxnID"],i["TxnNumber"],CustomerRef_ListID,CustomerRef_FullName,i["TxnDate"],i["RefNumber"],float(i["Subtotal"]),float(i["BalanceRemaining"]),i["IsPaid"]))
                except:
                    pass
    elif querytype == 'Customer':
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


