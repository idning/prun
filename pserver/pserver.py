#!/usr/bin/env python
#coding: utf-8
#file   : helloworld.py
#author : ning
#date   : 2013-03-13 09:42:39

#支持列目录功能.

import os
import sys
import socket
import re
import time

import tornado.ioloop
import tornado.web

PWD = os.path.dirname(os.path.realpath(__file__))
class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

#GET /q?q=a:b

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

        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        upstream = tornado.iostream.IOStream(s)
        upstream.connect((host, int(port)), start_tunnel)

# for pelican
def get_pelican_time(path):
    if os.path.isdir(path):
        return sys.maxint
    data = file(path).read()
    m = re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', data, re.DOTALL)
    if m:
        t = m.group(0)
        return time.mktime(time.strptime(t, '%Y-%m-%d %X'))
    return 0

def get_mtime(path):
    return os.path.getmtime(path)

def sort_fun(path):
    return 0

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        tornado.web.StaticFileHandler.initialize(self, path)

    def get(self, in_path='/', *args, **kwargs):
        path = self.parse_url_path(in_path)
        abspath = os.path.abspath(os.path.join(self.root, path))

        print 'root :', self.root
        print 'path :', path
        print 'read file :', abspath
        
        self.write('dir list for %s' % path)
        self.write('<hr>')

        if not os.path.isdir(abspath): 
            return tornado.web.StaticFileHandler.get(self, path)

        lst = os.listdir(abspath)
        lst = sorted(lst, reverse=True, key=lambda s: sort_fun(os.path.join(abspath, s)))
        for filename in lst:
            p = os.path.join(abspath, filename)
            if os.path.isdir(p):
                html = '<li><a href="%s/">%s/</a></br>\n' % (filename, filename)
            else:
                html = '<li><a href="%s">%s</a></br>\n' % (filename, filename)
            self.write(html)
        
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-p', '--port', type=int, default='8888')
    parser.add_argument('-r', '--root', default=os.path.join(PWD, '../'))
    parser.add_argument('-t', '--timefun', default='get_mtime')
    ARGS = parser.parse_args()

    global sort_fun
    sort_fun = eval(ARGS.timefun)

    application = tornado.web.Application([
        (r"/hello", HelloHandler),
        (r"/q", ProxyHandler),
        (r"/(.*)", MyStaticFileHandler, {'path': ARGS.root} ),
    ])
    application.listen(ARGS.port)
    tornado.ioloop.IOLoop.instance().start()

