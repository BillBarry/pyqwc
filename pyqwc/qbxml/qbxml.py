from lxml import etree

def iterative_query_request(requestID=1,iteratorID="",querytype="",MaxReturned=100,IncludeLineItems=False):
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
    irq = etree.SubElement(msg,querytype+'QueryRq',attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(MaxReturned)
    if querytype == 'Invoice' and IncludeLineItems:
        incitems = etree.SubElement(irq,'IncludeLineItems')
        incitems.text="true"
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    return requestxml

def invoice_query(requestID=1,iteratorID="",querytype="",fullname="",IncludeLineItems=False,MaxReturned=100):
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
    irq = etree.SubElement(msg,querytype+'QueryRq',attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(MaxReturned)

    mrt = etree.SubElement(irq,'EntityFilter')
    ef = etree.SubElement(mrt,'FullNameWithChildren')
    ef.text= str(fullname)
    if querytype == 'Invoice' and IncludeLineItems:
        incitems = etree.SubElement(irq,'IncludeLineItems')
        incitems.text="true"
    includelinkedtxns = etree.SubElement(irq,'IncludeLinkedTxns')
    includelinkedtxns.text="true"
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    return requestxml

