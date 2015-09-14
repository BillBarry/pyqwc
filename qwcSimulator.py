from suds.client import Client as SudsClient
import json
import time

with open('config.json') as json_config_file:
    config = json.load(json_config_file)


def runSimulator():
    url = 'http://127.0.0.1:8000/qwc?wsdl'
    print "simulator"
    client = SudsClient(url=url, cache=None)
    while True:
        returnArray = client.service.authenticate( strUserName = config['UserName'], strPassword= config['Password'])
        print 'returnArray[0]',returnArray[0]
        if returnArray and (returnArray[0][1] <> "none") and (returnArray[0][1] <> "nvu"):
            reqXML = client.service.sendRequestXML( ticket = str(returnArray[0][0]),strHCPResponse="",strCompanyFileName=returnArray[0][1],qbXMLCountry="",qbXMLMajorVers=8,qbXMLMinorVers=0)
            percentRemaining = client.service.receiveResponseXML( ticket = str(returnArray[0][0]),response="<xml>this is your response</xml>",hresult ="",message="")
        else:    
            time.sleep(15)
