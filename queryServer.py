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
    app.config['requestQueue'].put({'job':'retrieve_invoices'})
    return render_template('syncdb.html',data="retrieving invoices")

@app.route("/qwc/customer")
def retrieve_customers():
    app.config['requestQueue'].put({'job':'retrieve_customers'})
    return render_template('syncdb.html',data="retrieving customers")

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

