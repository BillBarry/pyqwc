from suds.client import Client as SudsClient
import json
import time

with open('config.json') as json_config_file:
    config = json.load(json_config_file)
    print "reading passwords in simulator"



def runSimulator():
    url = 'http://127.0.0.1:8000/qwc?wsdl'
    print "simulator"
    client = SudsClient(url=url, cache=None)
    strUserName = config['UserName']
    print strUserName
    while True:
        #returnArray = client.service.authenticate( strUserName = config['UserName'], strPassword= config['Password'])
        returnArray = client.service.authenticate( strUserName = config['UserName'], strPassword= config['Password'])
        print returnArray
        time.sleep(15)
