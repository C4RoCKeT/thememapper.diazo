from flask import Flask
from diazo.wsgi import DiazoMiddleware
from wsgiproxy.app import WSGIProxyApp
from tornado.wsgi import WSGIContainer
from tornado.web import Application,StaticFileHandler,FallbackHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import autoreload
import os
import thememapper

url = 'http://ping-win.nl'
rules_file = '/home/c4rocket/Documents/Projects/diazo-test/themes/dangled/rules.xml'
SERVER_NAME = '129.125.101.162'

class MyWSGIProxyApp(WSGIProxyApp):
    def setup_forwarded_environ(self, environ):
        super(MyWSGIProxyApp, self).setup_forwarded_environ(environ)
        environ['SERVER_NAME'] = SERVER_NAME
        environ['HTTP_HOST'] = 'ping-win.nl'

    def __call__(self, environ, start_response):
        return super(MyWSGIProxyApp, self).__call__(environ, start_response)

def start_diazo_server(port):
    app = Flask(__name__)
    app.wsgi_app = DiazoMiddleware(MyWSGIProxyApp(url),None,rules_file,prefix='/static',read_network=True)
    handlers = [
        (r'/static/(.*)', StaticFileHandler, {'path': os.path.dirname(rules_file)}),
        (r'/(.*)', FallbackHandler, {'fallback': WSGIContainer(app)})
        ]
    HTTPServer(Application(handlers)).listen(port)
    IOLoop.instance().start()
    ioloop = IOLoop.instance()
    #autoreload.watch(os.path.join(path, item))
    autoreload.start(ioloop)
    ioloop.start()
    
def main():
    print '========================'
    print '==== SERVER STARTED ===='
    print '========================'
    start_diazo_server(5000)

if __name__ == '__main__':
    main()