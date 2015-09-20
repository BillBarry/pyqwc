import json
import uuid
from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode, Iterable, ComplexModel
from spyne.protocol.soap import Soap11
from flask import Flask, request
from flask.ext.spyne import Spyne
import time
from lxml import etree
from configobj import ConfigObj
 
app = Flask(__name__)
spyne = Spyne(app)

config = ConfigObj('config.ini')


def returnxml(responseXML):
    return responseXML

@app.route("/api/xml")
def receivexml():
    #get the xml from the request
    reqXML = request.args.get('requestxml', '')
    print "request",request.data
    print "first hello"
    session_manager.queue_session({'reqXML':request,'callback':returnxml})



class qbwcSessionManager():
    def __init__(self, sessionQueue = []):
        # this is a first in last out queue, i.e. a stack
        self.sessionQueue = sessionQueue  

    def queue_session(self,msg):
        if 'ticket' not in msg or not msg['ticket']:
            ticket =  str(uuid.uuid1())
        else:
            ticket = msg['ticket']
        self.sessionQueue.append({"ticket":ticket,"reqXML":msg['reqXML'],"callback":msg["callback"]})
    
    def get_session(self):
        if self.sessionQueue:
            return self.sessionQueue[0]
        else:
            return ""
        
    def send_request(self,ticket):
        if self.sessionQueue:
            if ticket == self.sessionQueue[0]['ticket']:
                ret = self.sessionQueue[0]['reqXML']
                return ret
            else:
                print "tickets do not match. There is trouble somewhere"
                return ""
        
    def return_response(self,ticket, response):
        if ticket == self.sessionQueue[0]['ticket']:
            callback = self.sessionQueue[0]['callback']
            self.sessionQueue.pop(0)
            callback(ticket,response)
        else:
            app.logger.debug("tickets do not match. There is trouble somewhere")
            return ""

class QBWCService(spyne.Service):
    __target_namespace__ =  'http://developer.intuit.com/'
    __service_url_path__ = '/qwc'
    __in_protocol__ = Soap11(validator='lxml')
    __out_protocol__ = Soap11()
    
    @spyne.srpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate( strUserName, strPassword):

        """Authenticate the web connector to access this service.
        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication
        @return the completed array
        """
        returnArray = []
        # or maybe config should have a hash of usernames and salted hashed passwords
        if strUserName == config['qwc']['username'] and strPassword == config['qwc']['password']:
            print "authenticated",time.ctime()
            session = session_manager.get_session()
            if 'ticket' in session:
                returnArray.append(session['ticket'])
                returnArray.append(config['qwc']['qbwfilename']) # returning the filename indicates there is a request in the queue
            else:
                returnArray.append("none") # don't return a ticket if there are no requests
                returnArray.append("none") #returning "none" indicates there are no requests at the moment
        else:
            returnArray.append("no ticket") # don't return a ticket if username password does not authenticate
            returnArray.append('nvu')
        app.logger.debug('authenticate %s',returnArray)
        return returnArray

    @spyne.srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        app.logger.debug('clientVersion %s',strVersion)
        return ""

    @spyne.srpc(Unicode,  _returns=Unicode)
    def closeConnection( ticket ):
        """ used by web connector to indicate it is finished with update session
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        app.logger.debug('closeConnection %s',ticket)
        return "OK"

    @spyne.srpc(Unicode,Unicode,Unicode,  _returns=Unicode)
    def connectionError( ticket, hresult, message ):
        """ used by web connector to report errors connecting to Quickbooks
        @param ticket session token sent from this service to web connector
        @param hresult The HRESULT (in HEX) from the exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        app.logger.debug('connectionError %s %s %s', ticket, hresult, message)
        return "done"

    @spyne.srpc(Unicode,  _returns=Unicode)
    def getLastError( ticket ):
        """  Web connector error message
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        app.logger.debug('lasterror %s',ticket)
        return "Error message here!"


    @spyne.srpc(Unicode,Unicode,Unicode,Unicode,Integer,Integer,  _returns=Unicode)
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
        reqXML = session_manager.send_request(ticket)
        app.logger.debug('sendRequestXML %s %s',strHCPResponse,reqXML)
        return reqXML

    @spyne.srpc(Unicode,Unicode,Unicode,Unicode,  _returns=Integer)
    def receiveResponseXML( ticket, response, hresult, message ):
        """ contains data requested from Quickbooks
        @param ticket session token sent from this service to web connector
        @param response qbXML response from QuickBooks
        @param hresult The HRESULT (in HEX) from any exception 
        @param message error message
        @return string integer returned 100 means done anything less means there is more to come.
              where can we best get that information?
        """
        app.logger.debug('receiveResponseXML %s %s %s %s',ticket,response,hresult,message)
        session_manager.return_response(ticket,response)

        #need to make this return be 100 if we are really done.
        return 10
    

session_manager = qbwcSessionManager()





if __name__ == '__main__':
    app.run(port=8000, debug=False)

