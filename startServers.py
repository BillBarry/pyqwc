import multiprocessing
from flask import Flask
import queryServer
import pyQBWC
import qwcSimulator
import time

def  QuickBooksFacing():
    pyQBWC.app.run(port=8000,debug=True)
    
def WebFacing():
    queryServer.app.run(host='127.0.0.1',port=5000,debug=True)
    # having debug=True is throwing a lot of warnings

def qwc():
    qwcSimulator.runSimulator()
        
if __name__ == '__main__':
    jobs = []
    talktoquickbooks  = multiprocessing.Process(target=QuickBooksFacing)
    jobs.append(talktoquickbooks)
    webserver = multiprocessing.Process(target=WebFacing)
    jobs.append(webserver)
    simulator = multiprocessing.Process(target=qwc)
    jobs.append(simulator)
    talktoquickbooks.start()
    webserver.start()
    time.sleep(1)
    simulator.start()
