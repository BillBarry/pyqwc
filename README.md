This is a python application used to access Quickbooks.

It is very alpha software and has a mixture of application code and Quickbooks interface. As things settle down these will be separated but right now we are exploring the best way to separate them.

It currently consists of two servers. One server is a soap server facing the Quickbooks web connector. This is the one that is used to get information from Quickbooks. The second server faces the web and delivers the processed Qickbooks data. Both use the flask combined with spyne via the Flask-spyne python module. This allows the Quickbooks server to speak soap to the qwc. On the web facing side the intention is to have a regular html server for web requests and a soap server for speaking to Excel spreadsheets.


##guidance provided by
The QBWC [manual](https://developer-static.intuit.com/qbSDK-current/doc/PDF/QBWC_proguide.pdf)
ricardosasilva's [django-to-quickbooks-connector](https://github.com/ricardosasilva/django-to-quickbooks-connector/blob/master/mydjangoproject/qbwc/views.py)
The spyne Hello World [example](http://spyne.io/docs/2.10/manual/02_helloworld.html)
Flask-spyne module [examples](https://github.com/rayrapetyan/flask-spyne)

A file config.ini is needed but not included in the distribution. Here is an example.
'''
[qwc]
# the Quickbooks file you are accessing
qbwfilename = "c:\data\QBDATA\qbfilename.QBW"
#username and password used by quickbooks web connector to access your service
# username should be the same as in pyQBWC.qwc
username = "qbwcuser"
# password given here is entered when you install the pyQBWC.qwc file 
#double click the qwc file in Windows and Quickbooks will prompt you for the password
password = "gbwcpassword"
[sqlite]
dbfile = 'ourQB.db'
'''
