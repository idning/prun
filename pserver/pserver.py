#!/usr/bin/env python
#coding: utf-8
#file   : helloworld.py
#author : ning
#date   : 2013-03-13 09:42:39

#支持列目录功能.

import os
import sys
import socket

import tornado.ioloop
import tornado.web

PWD = os.path.dirname(os.path.realpath(__file__))
class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class ProxyHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        q = self.request.arguments['q'][0]
        print 'proxy: ', q

        host, port = q.split(':')
        #host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)
        upstream.connect((host, int(port)), start_tunnel)

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        tornado.web.StaticFileHandler.initialize(self, path)

    def get(self, in_path='/', *args, **kwargs):
        path = self.parse_url_path(in_path)
        abspath = os.path.abspath(os.path.join(self.root, path))

        print 'root :', self.root
        print 'path :', path
        print 'read file :', abspath
        
        if not os.path.isdir(abspath): 
            return tornado.web.StaticFileHandler.get(self, path)

        for filename in os.listdir(abspath):
            p = os.path.join(abspath, filename)
            if os.path.isdir(p):
                html = '<a href="%s/">%s/</a></br>\n' % (filename, filename)
            else:
                html = '<a href="%s">%s</a></br>\n' % (filename, filename)
            self.write(html)
        
application = tornado.web.Application([
    (r"/hello", HelloHandler),
    (r"/q", ProxyHandler),
    (r"/(.*)", MyStaticFileHandler, {'path': os.path.join(PWD, '../')} ),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

