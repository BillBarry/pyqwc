import json
import uuid
from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


with open('config.json') as json_config_file:
    config = json.load(json_config_file)
    print config
    
class QBWCService(ServiceBase):
    @srpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate( strUserName, strPassword):

        """Authenticate the web connector to access this service.
        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication
        @return the completed array
        """
        returnArray = []
        returnArray.append(str(uuid.uuid1()))
        # or maybe config should have a hash of usernames and salted hashed passwords
        if strUserName == config['UserName'] and strPassword == config['Password']:
            returnArray.append(config['qbwFilename'])
        else:
            returnArray.append('nvu')
        print 'authenticate'
        print strUserName
        print returnArray
        return returnArray

    @srpc(Unicode,  _returns=Unicode)
    def clientVersion( strVersion ):
        """ sends Web connector version to this service
        @param strVersion version of GB web connector
        @return what to do in case of Web connector updates itself
        """
        print 'clientVersion()'
        print strVersion
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
        print ticket
        print hresult
        print message
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
        print ticket
        print response
        print hresult
        print message
        return 100

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
        print 'sendRequestXML'
        print strHCPResponse
        xmlr = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" + \
               "<?qbxml version=\"8.0\"?>" + \
               "<QBXML>" + \
               "<QBXMLMsgsRq onError=\"stopOnError\">" + \
               "<InvoiceQueryRq requestID=\"4\">" + \
               "<MaxReturned>10</MaxReturned>" +\
               "</InvoiceQueryRq>" +\
               "</QBXMLMsgsRq>" + \
               "</QBXML>"
        return xmlr
    
    

application = Application([QBWCService], 'http://developer.intuit.com/',
                          in_protocol = Soap11(validator='lxml'),
                         out_protocol = Soap11(validator='lxml'))

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("Listening to http://127.0.0.1:8000")
    logging.info("wsdl is at http://localhost:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()
    
