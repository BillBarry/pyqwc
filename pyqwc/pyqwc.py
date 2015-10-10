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
from waitress import serve
import os
import logging
import redis

logging.basicConfig(level=logging.WARNING)
DEBUG2 = 8
logging.addLevelName(DEBUG2,"DEBUG2")

configfile = os.environ['qwcconfig']
config = ConfigObj(configfile)

rdb = walrus.Database(
    host=config['redis']['host'],
    port=config['redis']['port'], 
    password=config['redis']['password'],
    db=config['redis']['db'])
#? need to clear the hashes pointed to by waiting work first
rdb.Hash('iterativeWork').clear()
rdb.List('waitingWork').clear()

class QBWCService(ServiceBase):
    @srpc(Unicode,Unicode,_returns=Array(Unicode))
    def authenticate(strUserName,strPassword):
        """Authenticate the web connector to access this service.
        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication
        @return the completed array
        """
        returnArray = []
        if strUserName == config['qwc']['username'] and strPassword == config['qwc']['password']:
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
        logging.debug('authenticate %s',returnArray)
        return returnArray

    @srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        logging.debug('clientVersion %s',strVersion)
        return ""

    @srpc(Unicode,  _returns=Unicode)
    def closeConnection( ticket ):
        """ used by web connector to indicate it is finished with update session
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        logging.debug('closeConnection %s',ticket)
        return "OK"

    @srpc(Unicode,Unicode,Unicode,  _returns=Unicode)
    def connectionError( ticket, hresult, message ):
        """ used by web connector to report errors connecting to Quickbooks
        @param ticket session token sent from this service to web connector
        @param hresult The HRESULT (in HEX) from the exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        # need to push this error to the client. Should there be a message channel on Redis for this?
        logging.debug('connectionError %s %s %s', ticket, hresult, message)
        return "done"

    @srpc(Unicode,  _returns=Unicode)
    def getLastError( ticket ):
        """  Web connector error message
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        logging.debug('lasterror %s',ticket)
        return "Error message here!"


    @srpc(Unicode,Unicode,Unicode,Unicode,Integer,Integer,  _returns=Unicode)
    def sendRequestXML( ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers ):
        #?maybe we could hang here, wait for some xml and send it to qwc, that way shortening the wait
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
        logging.debug('sendRequestXML %s ',strHCPResponse)
        logging.log(DEBUG2,'sendRequestXML %s ',reqXML)
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
        logging.debug('receiveResponseXML %s %s %s',ticket,hresult,message)
        logging.log(DEBUG2,'receiveResponseXML %s',response)
        percent_done = session_manager.process_response(ticket,response)
        return percent_done


class qbwcSessionManager():
    def __init__(self):
        #requests are read from redis and responses are returned in redis
        self.redisdb= walrus.Database(
            host=config['redis']['host'],
            port=config['redis']['port'], 
            password=config['redis']['password'],
            db=config['redis']['db'])
        self.iterativeWork = self.redisdb.Hash('iterativeWork')
        self.waitingWork = self.redisdb.List('waitingWork')

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

        #?look for error responses here if you get an error, clear the redis keys and abort
        #?you don't know what is happening so better to bail out than try and fix things
        # first store it
        responsekey = 'response:'+str(ticket)
        self.responseStore = self.redisdb.List(responsekey)
        self.responseStore.append(response)        
        #check if it is iterative
        root = etree.fromstring(str(response))
        isIterator = root.xpath('boolean(//@iteratorID)')
        if isIterator:
            nticket = self.iterativeWork['ticket']
            if nticket != ticket:
                logging.debug("real problem here, abort?",ticket,nticket)
            reqXML = self.iterativeWork['reqXML']
            reqroot = etree.fromstring(str(reqXML))
            iteratorRemainingCount = int(root.xpath('string(//@iteratorRemainingCount)'))
            iteratorID = root.xpath('string(//@iteratorID)')
            logging.info("iteratorRemainingCount %s",iteratorRemainingCount)
            if iteratorRemainingCount:
                # update the iterativeWork hash reqXML
                iteratornode =  reqroot.xpath('//*[@iterator]')
                iteratornode[0].set('iterator', 'Continue')
                requestID = int(reqroot.xpath('//@requestID')[0])
                iteratornode[0].set('requestID', str(requestID+1))
                iteratornode[0].set('iteratorID', iteratorID)
                ntree = etree.ElementTree(reqroot)
                requestxml = etree.tostring(ntree, xml_declaration=True, encoding='UTF-8')                
                self.iterativeWork['reqXML'] = requestxml
                self.iterativeWork['ticket'] = ticket
                return 50  # is there any reason to return an accurate number here? something less than 100 is all that is needed.
            else:
                # clear the iterativeWork hash
                self.iterativeWork.clear()
                # create a finish response
                self.responseStore.append("TheEnd")        
                return 100 #100 percent done
        else:
            self.responseStore.append("TheEnd")        
            return 100 #100 percent done
                            
    def get_requestXML(self,ticket):
        if self.iterativeWork['reqXML']:
            reqXML = self.iterativeWork['reqXML']
            nticket = self.iterativeWork['ticket']
            if nticket != ticket:
                logging.info("error ticket mismatch")
        elif self.waitingWork:
            nticket = self.waitingWork.pop()
            wwh = self.redisdb.Hash(nticket)
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
application  = WsgiApplication(app)

    
def start_server():
    serve(wsgi_app, host=config['qwc']['host'], port=int(config['qwc']['port']))

if __name__ == '__main__':
    start_server()


