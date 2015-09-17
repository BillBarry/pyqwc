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
    app.config['requestQueue'].put({'reqXML':request})
    while True:    
        if not app.config['responseQueue'].empty():
            msg = app.config['responseQueue'].get()
            return render_template('syncdb.html',data=msg)
        else:
            time.sleep(1)


@app.route("/qwc/syncToDatabase")    
def syncToDatabase():
    app.config['requestQueue'].put({'job':'syncQBtoDB'})
    #send a note to pyQBWC side and have syncing done there.
    return render_template('syncdb.html',data="Syncing")


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

