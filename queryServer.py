from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode, Iterable, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from flask import Flask, render_template
from flask.ext.spyne import Spyne
from lxml import etree
import time

app = Flask(__name__, static_url_path='')
spyne = Spyne(app)

def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g
    return start

@app.route("/")
def main():
    return render_template('syncdb.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route("/qwc/invoice")
def retrieve_invoices():
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'InvoiceQueryRq',{'requestID':'4'})
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text="10"
    tree = etree.ElementTree(root)
    request = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print "sending request",request
    app.config['requestQueue'].put({'reqXML':request})
    print "watching for response"
    while True:    
        if not app.config['responseQueue'].empty():
            msg = app.config['responseQueue'].get()
            return render_template('syncdb.html',data=msg)
        else:
            time.sleep(1)


@app.route("/qwc/syncToDatabase")    
def request_all_invoices(requestID=0,iteratorID="",ticket=""):
    number_of_documents_to_retrieve_in_each_iteration = 2
    invoiceAttributes = {}
    if not requestID:
        invoiceAttributes['iterator'] = "Start"
    else:
        invoiceAttributes['iterator'] = "Continue"
    requestID +=1        
    invoiceAttributes['requestID'] = str(requestID)
    if iteratorID:
        invoiceAttributes['iteratorID'] = iteratorID

    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'InvoiceQueryRq',invoiceAttributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(number_of_documents_to_retrieve_in_each_iteration)
    tree = etree.ElementTree(root)
    request = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    qwc.session_manager.send_request(request,receive_all_invoices,ticket=ticket,updatePauseSeconds=0,minimumUpdateSeconds=20,MinimumRunEveryNSeconds=30)
    return 


def receive_all_invoices(ticket,responseXML):
    with open("responseout", "w") as file:
        file.write(responseXML)
    root = etree.fromstring(responseXML)
    # do something with the response, store it in a database, return it somewhere etc
    requestID = int(root.xpath('//InvoiceQueryRs/@requestID')[0])
    iteratorRemainingCount = int(root.xpath('//InvoiceQueryRs/@iteratorRemainingCount')[0])
    iteratorID = root.xpath('//InvoiceQueryRs/@iteratorID')[0]
    print iteratorRemainingCount
    if iteratorRemainingCount:
        request_all_invoices(requestID,iteratorID,ticket=ticket)


class SomeSoapService(spyne.Service):    
    __service_url_path__ = '/soap/someservice'
    __in_protocol__ = Soap11(validator='lxml')
    __out_protocol__ = Soap11()
    
    @spyne.srpc(Unicode, Integer, _returns=Iterable(Unicode))
    def echo(str, cnt):
        for i in range(cnt):
            yield str
            

if __name__ == "__main__":
    app.run(port=5000,debug=True)

