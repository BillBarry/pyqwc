import walrus
import uuid
from configobj import ConfigObj
import os


class pyqwcClient():
    def  __init__(self):
        configfile = os.environ['QWC_CONFIG_FILE']
        config = ConfigObj(configfile)
        self.redisdb = walrus.Database(
            host=config['redis']['host'],
            port=config['redis']['port'], 
            password=config['redis']['password'],
            db=config['redis']['db'])
        self.redisdb.flushdb()
        
    def sendxml(self,reqXML):
        #this puts the request into redis for the other half of the service to read and respond    
        self.redisdb.flushdb()
        waitingWork = self.redisdb.List('qwc:waitingWork')
        jobID =  "qwc:"+str(uuid.uuid1())
        self.responsekey = 'qwc:response:'+jobID
        self.responselist = self.redisdb.List(self.responsekey)
        waitingWork.append(jobID)
        wwh = self.redisdb.Hash(jobID)
        wwh['reqXML'] = reqXML

    def processResponse(self,processdata,optparam=""):
        pubsub = self.redisdb.pubsub()
        pubsub.subscribe([self.responsekey])
        for item in pubsub.listen():
            if item['data'] == "end":
                pubsub.unsubscribe()
                self.responselist.clear()
                print "unsubscribed and finished"
                break
            elif item['data'] == "data":
                data = self.responselist.pop()
                if optparam:
                    processdata(data,optparam)
                else:
                    processdata(data)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.redisdb.flushdb()

        
