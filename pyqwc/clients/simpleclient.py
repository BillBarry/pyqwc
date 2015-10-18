import walrus
import uuid
from lxml import etree
from configobj import ConfigObj
import walrus
import qbxml
import time

configfile = os.environ['qwcconfig']
config = ConfigObj(configfile)


# put some xml on the redis queue
redisdb = walrus.Database(
    host=config['redis']['host'],
    port=config['redis']['port'], 
    password=config['redis']['password'],
    db=config['redis']['db'])

waitingWork = redisdb.List('qwc:waitingWork')

jobID =  "qwc:"+str(uuid.uuid1())
waitingWork.append(jobID)
reqXML = qbxml.iterative_query_request(requestID=1,iteratorID="",querytype="Customer",IncludeLineItems=True,MaxReturned=100)
wwh = redisdb.Hash(jobID)
wwh['reqXML'] = reqXML

responsekey = 'qwc:response:'+jobID
responselist = redisdb.List(responsekey)

pubsub = redisdb.pubsub()
pubsub.subscribe([responsekey])

for item in pubsub.listen():
    if item['data'] == "end":
        pubsub.unsubscribe()
        print "unsubscribed and finished"
        break
    elif item['data'] == "data":
        data = responselist.pop()
        print data
    

        
