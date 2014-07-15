
this is a private proxy

we use a modified http CONNECT proxy. change it to a GET method.

pserver
=======

based on tornado: https://github.com/facebook/tornado.git

client(prun)
============

we use

    os.putenv('LD_PRELOAD', so)

to inject a so, hook the connect method of client application, so we can use:

    ./prun.py curl 'www.sina.com'

proxy
=====

a pure python proxy, no auth supported.
(i forget what do i want to do, maybe auth, maybe I need get a.com/xx proxy)

supported proxy
===============


http://127.0.0.1:8888                       #http  connect porxy
https://127.0.0.1:8888                      #https connect proxy

http://127.0.0.1:8888/q?q=                  #http  get connect proxy
https://127.0.0.1:8888/q?q=                 #https get connect proxy


more python proxy:
==================

http://proxies.xhaus.com/python/


