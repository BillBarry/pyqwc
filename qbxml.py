from lxml import etree

def invoice_request_iterative(requestID=1,iteratorID=""):
    number_of_documents_to_retrieve_in_each_iteration = 100
    attributes = {}
    if not iteratorID:
        attributes['iterator'] = "Start"
    else:
        attributes['iterator'] = "Continue"
        attributes['iteratorID'] = iteratorID        
    attributes['requestID'] = str(requestID)
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'InvoiceQueryRq',attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(number_of_documents_to_retrieve_in_each_iteration)
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    return requestxml

def customer_request_iterative(requestID=1,iteratorID=""):
    number_of_documents_to_retrieve_in_each_iteration = 100
    attributes = {}
    if not iteratorID:
        attributes['iterator'] = "Start"
    else:
        attributes['iterator'] = "Continue"
        attributes['iteratorID'] = iteratorID        
    attributes['requestID'] = str(requestID)
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'CustomerQueryRq',attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(number_of_documents_to_retrieve_in_each_iteration)
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    return requestxml

def customer_request_iterative(requestID=1,iteratorID=""):
    number_of_documents_to_retrieve_in_each_iteration = 100
    attributes = {}
    if not iteratorID:
        attributes['iterator'] = "Start"
    else:
        attributes['iterator'] = "Continue"
        attributes['iteratorID'] = iteratorID        
    attributes['requestID'] = str(requestID)
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'CustomerQueryRq',attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(number_of_documents_to_retrieve_in_each_iteration)
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    return requestxml

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

