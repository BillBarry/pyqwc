import multiprocessing
from flask import Flask
import queryServer
import pyQBWC

def  QuickBooksFacing():
    pyQBWC.qwcapp.run(port=8000)
    
def WebFacing():
    queryServer.app.run(host='127.0.0.1',port=5000,debug=True)
    # having debug=True is throwing a lot of warnings
    
if __name__ == '__main__':
    jobs = []
    talktoquickbooks  = multiprocessing.Process(target=QuickBooksFacing)
    jobs.append(talktoquickbooks)
    webserver = multiprocessing.Process(target=WebFacing)
    jobs.append(webserver)
    talktoquickbooks.start()
    webserver.start()
