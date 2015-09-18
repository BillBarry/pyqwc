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


@app.route("/qwc/<querytype>")
def retrieve_records(querytype):
    # prevent xss
    if  querytype == 'invoice' or querytype == 'customer' or querytype == 'item' or querytype == 'iteminventory':
        if querytype == 'iteminventory':
            querytype = 'ItemInventory'
        else:
            querytype = querytype.capitalize()        
        print 'retrive_records ',querytype
        app.config['requestQueue'].put({'job':'retrieve_records','querytype':querytype})
        return render_template('syncdb.html',data="retrieving "+querytype)

@app.route("/qwc/synctodatabase/<querytype>")    
def syncToDatabase(querytype):
    if  querytype == 'invoice' or querytype == 'customer' or querytype == 'item' or querytype == 'iteminventory':
        if querytype == 'iteminventory':
            querytype = 'ItemInventory'
        else:
            querytype = querytype.capitalize()        
        app.config['requestQueue'].put({'job':'syncQBtoDB','querytype':querytype})
        #send a note to pyQBWC side and have syncing done there.
        return render_template('syncdb.html',data="Syncing "+querytype)


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


    
