import uuid
from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode, Iterable, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.util.wsgi_wrapper import WsgiMounter
import time
from configobj import ConfigObj
import logging

config = ConfigObj('config.ini')

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
        if strUserName == config['qwc']['username'] and strPassword == config['qwc']['password']:
            ticket = str(uuid.uuid1())
            returnArray.append(ticket)
            returnArray.append(config['qwc']['qbwfilename']) # returning the filename indicates there is a request in the queue
            #returnArray.append(0)
            #returnArray.append(0)
            #returnArray.append(10)
        print 'authenticate ',returnArray, time.ctime()
        return returnArray

    @srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        print 'clientVersion ', strVersion
        return ""

    @srpc(Unicode,  _returns=Unicode)
    def closeConnection( ticket ):
        """ used by web connector to indicate it is finished with update session
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print 'closeConnection ',ticket
        return "OK"

    @srpc(Unicode,Unicode,Unicode,  _returns=Unicode)
    def connectionError( ticket, hresult, message ):
        """ used by web connector to report errors connecting to Quickbooks
        @param ticket session token sent from this service to web connector
        @param hresult The HRESULT (in HEX) from the exception 
        @param message error message
        @return string done indicating web service is finished.
        """
        print 'connectionError ', ticket, hresult, message
        return "done"

    @srpc(Unicode,  _returns=Unicode)
    def getLastError( ticket ):
        """  Web connector error message
        @param ticket session token sent from this service to web connector
        @return string displayed to user indicating status of web service
        """
        print 'lasterror ',ticket
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
        reqXML = ""
        print 'sendRequestXML ',time.ctime()
        #print 'sendRequestXML ',strHCPResponse,reqXML,time.ctime()
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
        print 'receiveResponseXML ',ticket,response,hresult,message,time.ctime

        return 10
    


qwcapp = Application([QBWCService],
    tns='http://developer.intuit.com/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)



if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.CRITICAL)
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiMounter({'qwc':qwcapp})

    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()

