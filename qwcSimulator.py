from suds.client import Client as SudsClient
import time
from lxml import etree
from configobj import ConfigObj
import uuid
import qbxml

config = ConfigObj('config.ini')
#  this barely simulates the Quickbooks web connector for testing purposes. the qwc is basically a SOAP client
# that sits between our application and Quickbooks. It gets info from Quickbooks and sends it  to our SOAP server (and vice versa)

def runSimulator():
    url = 'http://127.0.0.1:8000/qwc?wsdl'
    print "simulator"
    client = SudsClient(url=url, cache=None)
    while True:
        returnArray = client.service.authenticate( strUserName = config['qwc']['username'], strPassword= config['qwc']['password'])
        print 'returnArray[0]',returnArray[0]
        if returnArray and (returnArray[0][1] <> "none") and (returnArray[0][1] <> "nvu"):
            ticket = str(returnArray[0][0])
            reqXML = client.service.sendRequestXML(ticket,strHCPResponse="",strCompanyFileName=returnArray[0][1],qbXMLCountry="",qbXMLMajorVers=8,qbXMLMinorVers=0)
            print reqXML
            root = etree.fromstring(str(reqXML))
            isIterator = root.xpath('boolean(//QBXMLMsgsRq/*[1]/@iterator)')
            while isIterator:
                iterator = root.xpath('//QBXMLMsgsRq/*[1]/@iterator')[0]
                requestID = int(root.xpath('//InvoiceQueryRq/@requestID')[0])
                requestID +=1                    
                if iterator == 'Start':
                    iterator = 'Continue'
                    iteratorID  =  str(uuid.uuid1())
                    iteratorRemainingCount=20
                elif iterator == 'Continue':
                    
                    iteratorRemainingCount  -= 1
                responsexml = qbxml.make_fake_invoice(requestID,iteratorID,iteratorRemainingCount,iterator)
                percentRemaining = client.service.receiveResponseXML( ticket = ticket,response=responsexml,hresult ="",message="")
                time.sleep(5)
                reqXML = client.service.sendRequestXML(ticket,strHCPResponse="",strCompanyFileName=returnArray[0][1],qbXMLCountry="",qbXMLMajorVers=8,qbXMLMinorVers=0)
                print reqXML
                root = etree.fromstring(str(reqXML))
                isIterator = root.xpath('boolean(//QBXMLMsgsRq/*[1]/@iterator)')
            break
        else:    
            time.sleep(5)

