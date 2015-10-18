from pyqwc import qbxml
from pyqwc import clientlib

qwcClient = clientlib.pyqwcClient()
reqXML = qbxml.iterative_query_request(requestID=1,iteratorID="",querytype="Customer",IncludeLineItems=True,MaxReturned=100)
qwcClient.sendxml(reqXML)

def savedata(data):
    #print data
    print "received data"
qwcClient.processResponse(savedata)


    

        
