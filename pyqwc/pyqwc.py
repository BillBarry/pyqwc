import os
import uuid
import logging
from lxml import etree
from configobj import ConfigObj
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.application import Application
from spyne.server.wsgi import WsgiApplication
from spyne.model.primitive import Integer, Unicode
from spyne.model.complex import Iterable, ComplexModel, Array
from waitress import serve
import walrus
import time

configfile = os.environ['QWC_CONFIG_FILE']
config = ConfigObj(configfile)

DEBUG2 = 8
LEVELS = {'DEBUG2': DEBUG2,
          'DEBUG':logging.DEBUG,
          'INFO':logging.INFO,
          'WARNING':logging.WARNING,
          'ERROR':logging.ERROR,
          'CRITICAL':logging.CRITICAL,
          }
logging.addLevelName(DEBUG2,"DEBUG2")
logging.basicConfig(level=LEVELS[config['qwc']['loglevel'].upper()])


#rdb = walrus.Database(
#    host=config['redis']['host'],
#    port=config['redis']['port'], 
#    password=config['redis']['password'],
#    db=config['redis']['db'])
#clear any qwc keys accidentally leftover in redis
#keystodelete = rdb.keys(pattern='qwc:*')
#for k in keystodelete:
#    rdb.delete(k)

    
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
            if session_manager.inSession():
                returnArray.append("none")
                returnArray.append("busy")
                logging.warning('trying to authenticate during an open session')
            else:
                sessionticket = session_manager.setTicket()
                returnArray.append(sessionticket)
                returnArray.append(config['qwc']['qbwfilename']) # returning the filename indicates there is a request in the queue
                logging.warning('creating a new sessionTicket')
        else:
            returnArray.append("none") # don't return a ticket if username password does not authenticate
            returnArray.append('nvu')
        logging.warning('authenticate %s',returnArray)
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
        #session_manager.closeSession()
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
        #return "Error message here!"
        return "NoOp"



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
        logging.warning('sendRequestXML %s %s',time.ctime(),ticket)
        logging.warning('redis ticket %s',session_manager.inSession())
        reqXML = session_manager.get_reqXML(ticket)
        logging.log(DEBUG2,'sendRequestXML reqXML %s ',reqXML)
        logging.log(DEBUG2,'sendRequestXML strHCPResponse %s ',strHCPResponse)
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
        self.currentWork = self.redisdb.Hash('qwc:currentWork')
        self.waitingWork = self.redisdb.List('qwc:waitingWork')
        self.sessionKey = 'qwc:sessionTicket'

    def setTicket(self):
        sessionTicket = str(uuid.uuid1())
        self.redisdb.set(self.sessionKey,sessionTicket)
        return sessionTicket
    
    def clearTicket(self):
        sessionTicket = ""
        self.redisdb.set(self.sessionKey,sessionTicket)
        return sessionTicket
    
    def inSession(self):
        print self.redisdb.get(self.sessionKey)
        return self.redisdb.get(self.sessionKey)
    
    def closeSession(self):
        self.clearTicket()
    
    def is_iterative(self,reqXML):
        root = etree.fromstring(str(reqXML))
        isIterator = root.xpath('boolean(//@iterator)')
        return isIterator

    def process_response(self,ticket,response):
        #?look for error responses here if you get an error, clear the redis keys and abort
        #?you don't know what is happening so better to bail out than try and fix things
        # first store it
        reqID =  self.currentWork['reqID']
        responsekey = 'qwc:response:'+reqID
        self.responseStore = self.redisdb.List(responsekey)
        self.responseStore.append(response)
        logging.debug("storing response %s",responsekey)
        #check if it is iterative
        root = etree.fromstring(str(response))
        isIterator = root.xpath('boolean(//@iteratorID)')
        if isIterator:
            reqXML = self.currentWork['reqXML']
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
                nextreqXML = etree.tostring(ntree, xml_declaration=True, encoding='UTF-8')                
                self.currentWork['reqXML'] = nextreqXML
            else:
                # clear the currentWork hash
                self.currentWork.clear()
                # create a finish response
                self.responseStore.append("TheEnd")
        return 50 #this causes it to return to sendrequestXML, block and wait for more job requests

            
    def get_reqXML(self,ticket):
        if self.currentWork['reqXML']:
            return  self.currentWork['reqXML']
        else:
            logging.warning("block waiting for work in qwc:waitingWork")
            litem  = self.redisdb.blpop(['qwc:waitingWork'],timeout=50)
            if litem:
                reqID = litem[1]
                wwh = self.redisdb.Hash(reqID)
                reqXML = wwh['reqXML']
                self.currentWork['reqXML'] = reqXML
                self.currentWork['reqID'] = reqID
                logging.warning("got a request via blocking %s",reqID)
                wwh.clear()
                return reqXML
            else:
                logging.warning("timed out blocking on qwc:waitingWork")
                #self.clearTicket()
                return ""

                    
    def get_reqID(self,ticket):
        return  self.currentWork['reqID']


app = Application([QBWCService],
    tns='http://developer.intuit.com/',
    in_protocol=Soap11(validator='soft'),
    out_protocol=Soap11()
)
session_manager = qbwcSessionManager()
application  = WsgiApplication(app)

    
def start_server():
    serve(application, host=config['qwc']['host'], port=int(config['qwc']['port']))

if __name__ == '__main__':
    start_server()


