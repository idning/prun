
this is a private proxy 

we use a modified http CONNECT proxy. change it to a GET method. 

server
======

tornado: https://github.com/facebook/tornado.git

client
======

we use 

    os.putenv('LD_PRELOAD', so)

to inject a so, hook the connect method of client application, so we can use:

    ./prun.py curl 'www.sina.com'


