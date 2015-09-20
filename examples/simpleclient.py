import requests

requestxml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="8.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceQueryRq>
      <MaxReturned>"2"</MaxReturned>
      <IncludeLineItems>true</IncludeLineItems>
    </InvoiceQueryRq>   
  </QBXMLMsgsRq>
</QBXML>
"""

payload = {"requestxml":requestxml}
r = requests.get('http://localhost:8000/api/xml',params=payload)
print r
