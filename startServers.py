import multiprocessing
import logging
from flask import Flask
from wsgiref.simple_server import make_server
import queryServer
import pyQBWC


def  QuickBooksFacing():
    pyQBWC.qwcapp.run(port=8000)
'''  
    logging.basicConfig(level=logging.INFO)
    logging.info("Listening to http://127.0.0.1:8000")
    logging.info("wsdl is at http://localhost:8000/?wsdl")
    server = make_server('127.0.0.1', 8000, pyQBWC.wsgi_application)
    server.serve_forever()
'''
    
def WebFacing():
    queryServer.app.run(host='127.0.0.1',port=5000,debug=True)



if __name__ == '__main__':
    jobs = []
    talktoquickbooks  = multiprocessing.Process(target=QuickBooksFacing)
    jobs.append(talktoquickbooks)
    webserver = multiprocessing.Process(target=WebFacing)
    jobs.append(webserver)
    talktoquickbooks.start()
    webserver.start()
