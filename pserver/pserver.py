#!/usr/bin/env python
#coding: utf-8
#file   : helloworld.py
#author : ning
#date   : 2013-03-13 09:42:39

import os
import sys
import socket
import re
import time
import ssl


import argparse
import tornado.web
import tornado.httpserver
import tornado.httpclient

ARGS = None

PWD = os.path.dirname(os.path.realpath(__file__))
class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

#GET /q?q=a:b

class MyProxyHandler(tornado.web.RequestHandler):
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

class MyTunnelHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT']

    @tornado.web.asynchronous
    def connect(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream
        print 'CONNECT %s:%s' % (host, port)

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

        def ddd(data=None):
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        def start_tunnel():
            method = 'CONNECT '
            conn_str = "%s%s:%s HTTP/1.0\r\n\r\n" % (method, host, port);
            print 'write', conn_str
            print 'write', upstream.write_to_fd(conn_str)

            # while True:
                # print 'read', upstream.read_from_fd()

            print upstream.read_until('\r\n\r\n', ddd)


        #https://127.0.0.1:8888/q?q=
        m = re.match('(.*?)://(.*?):(.*?)/(.*?)', ARGS.upstream)
        upstream_protocl, upstream_host, upstream_port, connect_str = m.groups()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        print 'setup tunnel to %s' % ARGS.upstream

        if upstream_protocl == 'https':
            upstream = tornado.iostream.SSLIOStream(s,
                ssl_options= dict(
                    # ca_certs="/home/ning/idning-github/prun/conf/www.ning.com.cert",
                    ca_certs=None,
                    cert_reqs=ssl.CERT_NONE))
        else:
            upstream = tornado.iostream.IOStream(s)

        upstream.connect((upstream_host, int(upstream_port)), start_tunnel)

    @tornado.web.asynchronous
    def _get(self):
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
            method = 'CONNECT'
            conn_str = "%s%s:%s HTTP/1.0\r\n\r\n" % (s, host, port);
            upstream.write(conn_str)

            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # stream = iostream.IOStream(s)
        upstream = iostream.SSLIOStream(s,
            ssl_options= dict(
                ca_certs="/home/ning/idning-github/prun/conf/www.ning.com.cert",
                cert_reqs=ssl.CERT_NONE))

        # upstream = tornado.iostream.IOStream(s)
        upstream.connect((host, int(port)), start_tunnel)

class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT']

    @tornado.web.asynchronous
    def get(self):
        if not self.handle_auth():
            return

        print 'get %s' % self.request.uri
        def handle_response(response):
            if response.error and not isinstance(response.error,
                    tornado.httpclient.HTTPError):
                self.set_status(500)
                self.write('Internal server error:\n' + str(response.error))
            else:
                self.set_status(response.code)
                for header in ('Date', 'Cache-Control', 'Server',
                        'Content-Type', 'Location'):
                    v = response.headers.get(header)
                    if v:
                        self.set_header(header, v)
                if response.body:
                    self.write(response.body)
            self.finish()

        req = tornado.httpclient.HTTPRequest(url=self.request.uri,
            method=self.request.method, body=self.request.body,
            headers=self.request.headers, follow_redirects=False,
            allow_nonstandard_methods=True)

        client = tornado.httpclient.AsyncHTTPClient()
        try:
            client.fetch(req, handle_response)
        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write('Internal server error:\n' + str(e))
                self.finish()

    @tornado.web.asynchronous
    def post(self):
        return self.get()

    def handle_auth(self):
        return True

        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        print self.request

        if 'Proxy-Authorization' in self.request.headers:
            auth = self.request.headers['Proxy-Authorization']
            import base64
            user_passwd = base64.b64decode(auth.split()[1])
            print auth, user_passwd
            user, passwd = user_passwd.split(':', 1)

            if user == 'ning' and passwd == 'passwd':
                return True

        client.write('HTTP/1.0 407 Proxy Authentication Required\r\n')
        client.write('proxy-Authenticate: Basic\r\n')
        client.write('\r\n')

        return False

    @tornado.web.asynchronous
    def connect(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream
        print 'connect %s:%s' % (host, port)

        if not self.handle_auth():
            return

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

def main():
    global ARGS

    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-p', '--port', type=int, default='8888')
    parser.add_argument('--https', default=None, help="htttps hostname, used tofind certs")
    parser.add_argument('--upstream',  default='', help='upstream of tunnel, http://x.com:8888 | https://x.com:8888')

    ARGS = parser.parse_args()

    if ARGS.upstream:   #as a tunnel server
        application = tornado.web.Application([
            (r"/hello", HelloHandler),
            (r".*", MyTunnelHandler),
        ])
    else:               # as a proxy server
        application = tornado.web.Application([
            (r"/hello", HelloHandler),
            (r"/q", MyProxyHandler),
            (r".*", ProxyHandler),
        ])

    #enable https.
    http_server = tornado.httpserver.HTTPServer(application)
    if ARGS.https:
        ssl_options = {
            "certfile": "conf/%s.cert" % ARGS.https,
            "keyfile": "conf/%s.key" % ARGS.https,
        }

        if not os.path.exists(ssl_options['certfile']):
            print 'cert %s not exist!' % ssl_options['certfile']
            exit(1)
        if not os.path.exists(ssl_options['keyfile']):
            print 'keyfile %s not exist!' % ssl_options['keyfile']
            exit(1)

        http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options)

    http_server.listen(ARGS.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
