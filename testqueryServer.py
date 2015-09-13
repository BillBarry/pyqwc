from suds.client import Client as SudsClient
import requests

url = 'http://127.0.0.1:5000/soap/someservice?wsdl'
client = SudsClient(url=url, cache=None)
r = client.service.echo(str='hello world', cnt=3)
print r
