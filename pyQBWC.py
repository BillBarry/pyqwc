import json
import uuid
from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from lxml import etree

with open('config.json') as json_config_file:
    config = json.load(json_config_file)
    print config



class qbwcSessionManager():
    def __init__(self, sessionQueue = []):
        self.sessionQueue = sessionQueue  # this is a first in last out queue, i.e. a stack

    def send_request(self,reqXML,callback,ticket="",updatePauseSeconds=None,minimumUpdateSeconds=15,MinimumRunEveryNSeconds=15):
        #when called create a session ticket and stuff it in the store
        if not ticket:
            ticket =  str(uuid.uuid1())
        self.sessionQueue.append({"ticket":ticket,"reqXML":reqXML,"callback":callback,"updatePauseSeconds":updatePauseSeconds,"minimumUpdateSeconds":minimumUpdateSeconds,"MinimumRunEveryNSeconds":MinimumRunEveryNSeconds})

    def get_session(self):
        if self.sessionQueue:
            return self.sessionQueue[0]
        else:
            return ""
    
        
    def get_request(self,ticket):
        if ticket == self.sessionQueue[0]['ticket']:
            return self.sessionQueue[0]['reqXML']
        else:
            print "tickets do not match. There is trouble somewhere"
            return ""
        
    def return_response(self,ticket, response):
        #perform the callback to return the data to the requestor
        #remove the session from the queue
        if ticket == self.sessionQueue[0]['ticket']:
            self.sessionQueue[0]['callback'](ticket, response)
            self.sessionQueue.pop(0)
        else:
            print "tickets do not match. There is trouble somewhere"
            return ""

        
    
session_manager = qbwcSessionManager()

        
class QBWCService(ServiceBase):
    @srpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate( strUserName, strPassword):

        """Authenticate the web connector to access this service.
        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication
        @return the completed array
        """
        returnArray = []
        # or maybe config should have a hash of usernames and salted hashed passwords
        if strUserName == config['UserName'] and strPassword == config['Password']:
            session = session_manager.get_session()
            ticket = session['ticket']
            returnArray.append(ticket)
            if ticket:
                returnArray.append(config['qbwFilename']) # returning the filename indicates there is a request in the queue
            else:
                returnArray.append("none") #returning "none" indicates there are no requests at the moment
        else:
            returnArray.append("") # don't return a sessionid if username password does not authenticate
            returnArray.append('nvu')
        #returnArray.append(str(session['updatePauseSeconds']))
        returnArray.append("")
        returnArray.append("")
   #     returnArray.append(str(session['minimumUpdateSeconds']))
        returnArray.append(str(session['MinimumRunEveryNSeconds']))        
        print 'authenticate'
        #print strUserName
        #print returnArray
        return returnArray

    @srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        print 'clientVersion()'
        #print strVersion
        return ""

    @srpc(Unicode,  _returns=Unicode)
    def closeConnection( ticket ):
        """ used by web connector to indicate it is finished with update session
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print 'closeConnection()'
        print ticket
        return "OK"

    @srpc(Unicode,Unicode,Unicode,  _returns=Unicode)
    def connectionError( ticket, hresult, message ):
        """ used by web connector to report errors connecting to Quickbooks
        @param ticket session token sent from this service to web connector
        @param hresult The HRESULT (in HEX) from the exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        print 'connectionError'
        #print ticket
        #print hresult
        #print message
        return "done"

    @srpc(Unicode,  _returns=Unicode)
    def getLastError( ticket ):
        """ sends Web connector version to this service
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print 'lasterror'
        print ticket
        return "Error message here!"


    @srpc(Unicode,Unicode,Unicode,Unicode,Integer,Integer,  _returns=Unicode)
    def sendRequestXML( ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers ):
        """ send request via web connector to Quickbooks
        @param ticket session token sent from this service to web connector
        @param strHCPResponse qbXML response from QuickBooks
        @param strCompanyFileName The Quickbooks file to get the data from
        @param qbXMLCountry the country version of QuickBooks
        @param qbXMLMajorVers Major version number of the request processor qbXML 
        @param qbXMLMinorVers Minor version number of the request processor qbXML 
        @return string containing the request if there is one or a NoOp
        """
        reqXML = session_manager.get_request(ticket)
        print 'sendRequestXML'
        #print strHCPResponse
        print reqXML
        return reqXML

    @srpc(Unicode,Unicode,Unicode,Unicode,  _returns=Integer)
    def receiveResponseXML( ticket, response, hresult, message ):
        """ contains data requested from Quickbooks
        @param ticket session token sent from this service to web connector
        @param response qbXML response from QuickBooks
        @param hresult The HRESULT (in HEX) from any exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        print 'receiveResponseXML'
        #print ticket
        #print response
        #print hresult
        #print message
        session_manager.return_response(ticket,response)
        return 10

        

def print_invoices(responseXML):
    print "printing invoices"
    print responseXML
    return

def retrieve_invoices():
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,'InvoiceQueryRq',{'requestID':'4'})
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text="10"
    tree = etree.ElementTree(root)
    request = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    session_manager.send_request(request,print_invoices)
    return 

def receive_all_invoices(ticket,responseXML):
    print responseXML
    root = etree.fromstring(responseXML)
    # do something with the response, store it in a database, return it somewhere etc
    requestID = int(root.xpath('//InvoiceQueryRs/@requestID')[0])
    iteratorRemainingCount = int(root.xpath('//InvoiceQueryRs/@iteratorRemainingCount')[0])
    iteratorID = root.xpath('//InvoiceQueryRs/@iteratorID')[0]
    print iteratorRemainingCount
    if iteratorRemainingCount:
        request_all_invoices(requestID,iteratorID,ticket=ticket)
    
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
    session_manager.send_request(request,receive_all_invoices,ticket=ticket,updatePauseSeconds=0,minimumUpdateSeconds=15,MinimumRunEveryNSeconds=20)
    return 

        

application = Application([QBWCService], 'http://developer.intuit.com/',
                          in_protocol = Soap11(validator='lxml'),
                         out_protocol = Soap11())

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)

    logging.info("Listening to http://127.0.0.1:8000")
    logging.info("wsdl is at http://localhost:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)

    request_all_invoices()
    server.serve_forever()
    
