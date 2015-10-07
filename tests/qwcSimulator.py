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
    url = 'http://127.0.0.1:8000/?wsdl'
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
                    iteratorRemainingCount=2
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



def make_fake_invoice(requestID=1,iteratorID="",iteratorRemainingCount="",iterator=""):
    requestxml = '''<?xml version="1.0" ?>
<QBXML>
<QBXMLMsgsRs>
<InvoiceQueryRs requestID="%s" statusCode="0" iterator="%s" statusSeverity="Info" statusMessage="Status OK" iteratorRemainingCount="%s" iteratorID="{%s}">
<InvoiceRet>
<TxnID>1-1248977778</TxnID>
<TimeCreated>2015-07-30T16:14:18-06:00</TimeCreated>
<TimeModified>2015-01-13T13:43:19-06:00</TimeModified>
<EditSequence>1248839392</EditSequence>
<TxnNumber>1</TxnNumber>
<CustomerRef>
<ListID>8000003C-12489377329</ListID>
<FullName>NLC Products</FullName>
</CustomerRef>
<ARAccountRef>
<ListID>80000884-12997645215</ListID>
<FullName>Accounts Receivable</FullName>
</ARAccountRef>
<TemplateRef>
<ListID>80000543-19785437449</ListID>
<FullName>Our Company Invoice</FullName>
</TemplateRef>
<TxnDate>2015-09-15</TxnDate>
<RefNumber>921</RefNumber>
<BillAddress>
<Addr1>Conglomerate Inc.</Addr1>
<Addr2></Addr2>
<Addr3>PO Box 44432</Addr3>
<City>Big City</City>
<State>AL</State>
<PostalCode>12888</PostalCode>
</BillAddress>
<BillAddressBlock>
<Addr1>Conglomerate Inc.</Addr1>
<Addr2></Addr2>
<Addr3>PO Box 44432</Addr3>
<Addr4>Big City, AL 12888</Addr4>
</BillAddressBlock>
<ShipAddress>
<Addr1>Conglomerate</Addr1>
<Addr2>Good Customer</Addr2>
<Addr3>Old Rd.</Addr3>
<City>Example</City>
<State>AL</State>
<PostalCode>12345</PostalCode>
</ShipAddress>
<ShipAddressBlock>
<Addr1>Conglomerate</Addr1>
<Addr2>Good Customer</Addr2>
<Addr3>Old Rd.</Addr3>
<Addr4>Example, AL 12345</Addr4>
</ShipAddressBlock>
<IsPending>false</IsPending>
<IsFinanceCharge>false</IsFinanceCharge>
<PONumber>74508</PONumber>
<TermsRef>
<ListID>80000017-1388382074</ListID>
<FullName>Net 30</FullName>
</TermsRef>
<DueDate>2015-08-31</DueDate>
<SalesRepRef>
<ListID>80000015-1243334588</ListID>
<FullName>FB</FullName>
</SalesRepRef>
<ShipDate>2015-09-17</ShipDate>
<ShipMethodRef>
<ListID>80000006-1248382054</ListID>
<FullName>British Post</FullName>
</ShipMethodRef>
<Subtotal>150.00</Subtotal>
<SalesTaxPercentage>0.00</SalesTaxPercentage>
<SalesTaxTotal>0.00</SalesTaxTotal>
<AppliedAmount>-125.00</AppliedAmount>
<BalanceRemaining>0.00</BalanceRemaining>
<IsPaid>true</IsPaid>
<CustomerMsgRef>
<ListID>80000008-1234882073</ListID>
<FullName>A Custome</FullName>
</CustomerMsgRef>
<IsToBePrinted>false</IsToBePrinted>
<IsToBeEmailed>true</IsToBeEmailed>
</InvoiceRet>
</InvoiceQueryRs>
</QBXMLMsgsRs>
</QBXML>
''' % (requestID,iterator,iteratorRemainingCount,iteratorID)
    return requestxml

            
