import uuid
import walrus
from spyne.application import Application
from spyne.service import ServiceBase
from spyne.model.primitive import Integer, Unicode
from spyne.model.complex import Iterable, ComplexModel, Array
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
import time
from lxml import etree
from configobj import ConfigObj
from spyne.server.wsgi import WsgiApplication

import logging
logging.basicConfig(level=logging.INFO)

config = ConfigObj('config.ini')

class QBWCService(ServiceBase):
    @srpc(Unicode,Unicode,_returns=Array(Unicode))
    def authenticate(strUserName,strPassword):
        """Authenticate the web connector to access this service.
        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication
        @return the completed array
        """
        returnArray = []
        # or maybe config should have a hash of usernames and salted hashed passwords
        if strUserName == config['qwc']['username'] and strPassword == config['qwc']['password']:
            print "authenticated",time.ctime()
            ticket = session_manager.get_ticket()
            if ticket:
                returnArray.append(ticket)
                returnArray.append(config['qwc']['qbwfilename']) # returning the filename indicates there is a request in the queue
            else:
                returnArray.append("none") # don't return a ticket if there are no requests
                returnArray.append("none") #returning "none" indicates there are no requests at the moment
        else:
            returnArray.append("no ticket") # don't return a ticket if username password does not authenticate
            returnArray.append('nvu')
        print('authenticate %s',returnArray)
        return returnArray

    @srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        app.logger.debug('clientVersion %s',strVersion)
        return ""

    @srpc(Unicode,  _returns=Unicode)
    def closeConnection( ticket ):
        """ used by web connector to indicate it is finished with update session
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print('closeConnection %s',ticket)
        return "OK"

    @srpc(Unicode,Unicode,Unicode,  _returns=Unicode)
    def connectionError( ticket, hresult, message ):
        """ used by web connector to report errors connecting to Quickbooks
        @param ticket session token sent from this service to web connector
        @param hresult The HRESULT (in HEX) from the exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        print('connectionError %s %s %s', ticket, hresult, message)
        return "done"

    @srpc(Unicode,  _returns=Unicode)
    def getLastError( ticket ):
        """  Web connector error message
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print('lasterror %s',ticket)
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
        reqXML = session_manager.get_requestXML(ticket)
        print('sendRequestXML %s %s',strHCPResponse,reqXML)
        return reqXML

    @srpc(Unicode,Unicode,Unicode,Unicode,  _returns=Integer)
    def receiveResponseXML( ticket, response, hresult, message ):
        """ contains data requested from Quickbooks
        @param ticket session token sent from this service to web connector
        @param response qbXML response from QuickBooks
        @param hresult The HRESULT (in HEX) from any exception 
        @param message error message
        @return string integer returned 100 means done anything less means there is more to come.
              where can we best get that information?
        """
        print('receiveResponseXML %s %s %s %s',ticket,response,hresult,message)
        
        percent_done = session_manager.process_response(ticket,response)
        #need to make this return be 100 if we are really done.
        return percent_done


class qbwcSessionManager():
    def __init__(self):
        # this is a first in last out queue, i.e. a stack
        self.db = walrus.Walrus(host='localhost', port=6379, db=0)
        self.iterativeWork = self.db.Hash('iterativeWork')
        self.waitingWork = self.db.List('waitingWork')

    def get_ticket(self):
        if self.waitingWork:
            ticket = self.waitingWork[0]
            return ticket
        else:
            return ""
        
    def is_iterative(self,reqXML):
        root = etree.fromstring(str(reqXML))
        isIterator = root.xpath('boolean(//@iterator)')
        return isIterator

    def process_response(self,ticket,response):
        # first store it
        responsekey = 'response:'+str(ticket)
        self.responseStore = self.db.List(responsekey)
        self.responseStore.append(response)        
        #check if it is iterative
        root = etree.fromstring(str(response))
        isIterator = root.xpath('boolean(//@iterator)')
        if isIterator:
            nticket = self.iterativeWork['ticket']
            if nticket != ticket:
                print "real problem here, abort?"
            reqXML = self.iterativeWork['reqXML']
            reqroot = etree.fromstring(str(reqXML))
            iteratorRemainingCount = int(root.xpath('string(//@iteratorRemainingCount)'))
            if iteratorRemainingCount:
                # update the iterativeWork hash reqXML
                iteratornode =  reqroot.xpath('//*[@iterator]')
                iteratornode[0].set('iterator', 'Continue')
                requestID = int(reqroot.xpath('//@requestID')[0])
                iteratornode[0].set('requestID', str(requestID+1))
                ntree = etree.ElementTree(reqroot)
                requestxml = etree.tostring(ntree, xml_declaration=True, encoding='UTF-8')
                self.iterativeWork['reqXML'] = requestxml
                return 50
            else:
                # clear the iterativeWork hash
                self.iterativeWork.clear()
                # create a finish response
                self.responseStore.append("TheEnd")        
                return 100 #100 percent done
               
            
    def get_requestXML(self,ticket):
        if self.iterativeWork['reqXML']:
            reqXML = self.iterativeWork['reqXML']
            nticket = self.iterativeWork['ticket']
            if nticket != ticket:
                print "error ticket mismatch"
        elif self.waitingWork:
            nticket = self.waitingWork.pop()
            print 'waitingWork list',self.waitingWork
            wwh = self.db.Hash(nticket)
            reqXML = wwh['reqXML']
            wwh.clear()
            if self.is_iterative(reqXML):
                # save it to iterativeWork hash
                self.iterativeWork['reqXML'] = reqXML
                self.iterativeWork['ticket'] = nticket
        else:
            reqXML = ""
        return reqXML
        


app = Application([QBWCService],
    tns='http://developer.intuit.com/',
    in_protocol=Soap11(validator='soft'),
    out_protocol=Soap11()
)
session_manager = qbwcSessionManager()

if __name__ == '__main__':

    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(app)
    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()

