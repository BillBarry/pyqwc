import walrus
import uuid
from lxml import etree
from configobj import ConfigObj
import walrus
import tests.qbxml as qbxml
import time

# put some xml on the redis queue
db = walrus.Walrus(host='localhost', port=6379, db=0)
waitingWork = db.List('waitingWork')
ticket =  str(uuid.uuid1())
waitingWork.append(ticket)
reqXML = qbxml.iterative_query_request(requestID=1,iteratorID="",querytype="Invoice")
wwh = db.Hash(ticket)
wwh['reqXML'] = reqXML

responsekey = 'response:'+ticket
responselist = db.List(responsekey)
while True:
    if len(responselist):
        data = responselist.pop()
        print data
        if data == "TheEnd":
            print "The End"
            responselist.clear()
            break
    else:
        time.sleep(1)
        
