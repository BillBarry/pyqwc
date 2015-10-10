This is a python application used to access QuickBooks Desktop.

It is alpha software, beware.

To access Quickbooks this module uses the  `Quickbooks Web Connector <https://developer.intuit.com/docs/quickbooks_web_connector>`_ . The design of the QuickBooks Web Connector (QWC)  determines the underlying structure of this module.

The core of this is a soap server, called pyqwc. pyqwc takes requests from the user/client in XML, passes those off to QuickBooks via the QWC. It then takes the XML response from  QWC and passes them back to the user/client. This is a very asyncronous process because pyqwc does not directly contact the QWC, it instead has to wait for the QWC to contact it. To handle this asynchronous process, all messages are passed back and forth via Redis.  The request XML is placed in a specific Redis list and the response is passed back in another Redis list.

That describes the base layer, a soap server that basically passes messages back and forth between Redis and the QWC.  Above that base layer you can build any type of client to generate the XML requests, put them in Redis and retrieve the responses back from Redis. There are examples of clients in the clients subdirectory.

The soap server is written in python using the Spyne module and can be deployed using WSGI.

In order for QuickBooks to use the QWC, you must install a qwc file. An example is included.

Guidance provided by
--------------------

The QBWC `programmer's guide. <https://developer-static.intuit.com/qbSDK-current/doc/PDF/QBWC_proguide.pdf>`_

ricardosasilva's `django-to-quickbooks-connector <https://github.com/ricardosasilva/django-to-quickbooks-connector/blob/master/mydjangoproject/qbwc/views.py>`_

The spyne Hello World `example. <http://spyne.io/docs/2.10/manual/02_helloworld.html>`_

Reference source for `QBooks SDK. <https://developer-static.intuit.com/qbSDK-current/Common/newOSR/index.html>`_

Nice explanation on how to `install the qwc file. <http://www.nsoftware.com/kb/articles/qbwc.rst>`_

A file config.ini is needed but not included in the distribution. Here is an example.

::

   
   [qwc]
   # the Quickbooks file you are accessing
   qbwfilename = "c:\data\QBDATA\qbfilename.QBW"

   #username and password used by quickbooks web connector to access your service
   # username should be the same as in pyQBWC.qwc
   username = "qbwcuser"
   # password given here is entered when you install the pyqwc.qwc file 
   #double click the qwc file in Windows and Quickbooks will prompt you for the password
   password = "gbwcpassword"
   [sqlite]
   dbfile = 'ourQB.db'
   [redis]
   host = '127.0.0.1'
   port = 6379
   password = ""
   db = 0


