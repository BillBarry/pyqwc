import multiprocessing
from flask import Flask
import pyQBWC
import qwcSimulator
import time

# this is the script to start everything up. It starts two servers
# in two separate processes.
# by uncommenting the last three lines it can also start a third client process that simulates the Quickbooks web connector for testing.

def  QuickBooksFacing():
    pyQBWC.app.run(host="127.0.0.1",port=8000,debug=False)
    
def qwc():
    qwcSimulator.runSimulator()
        
if __name__ == '__main__':
    jobs = []
    talktoquickbooks = multiprocessing.Process(target=QuickBooksFacing)
    jobs.append(talktoquickbooks)
    simulator = multiprocessing.Process(target=qwc)
    jobs.append(simulator)
    talktoquickbooks.start()
    time.sleep(3)
    simulator.start()
