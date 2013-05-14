from flask import Flask
from diazo.wsgi import DiazoMiddleware
from wsgiproxy.app import WSGIProxyApp
from tornado.wsgi import WSGIContainer
from tornado.web import Application,StaticFileHandler,FallbackHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import autoreload
import optparse
import socket
from urlparse import urlparse

class MyWSGIProxyApp(WSGIProxyApp):
    
    global server_name,http_host
    
    def setup_forwarded_environ(self, environ):
        super(MyWSGIProxyApp, self).setup_forwarded_environ(environ)
        environ['SERVER_NAME'] = server_name
        environ['HTTP_HOST'] = http_host

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = '127.0.0.1'
        return super(MyWSGIProxyApp, self).__call__(environ, start_response)
    
class Mapper:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

def init(mapper):
    global http_host
    global server_name
    if mapper.rules_path != '':
        if mapper.diazo_port != '' and mapper.content_url != '':
            http_host = urlparse(mapper.content_url).netloc
            server_name = socket.gethostbyname(http_host)
        else:
            raise Exception("Error: arguments can't be empty.")
    else:
        raise Exception("Error: You should specify a rules file.")

        
def get_application(mapper):
    try:
        init(mapper)
        app = Flask(__name__)
        app.wsgi_app = DiazoMiddleware(MyWSGIProxyApp(mapper.content_url),None,mapper.rules_path,prefix='/thememapper_static',read_network=True,update_content_length=True,debug=True)
        handlers = [
            (r'/thememapper_static/(.*)', StaticFileHandler, {'path': mapper.static_path}),
            (r'/(.*)', FallbackHandler, {'fallback': WSGIContainer(app)})
            ]
        return Application(handlers)
    except Exception as e:
        print e
        return False
        
def start_diazo_server(mapper):
    app = get_application(mapper)
    if app is not False:
        print "Starting diazo on http://0.0.0.0:" + mapper.diazo_port
        HTTPServer(app).listen(mapper.diazo_port)
        ioloop = IOLoop.instance()
        autoreload.add_reload_hook(reload)
        autoreload.start(ioloop)
        ioloop.start()
        
def reload():
    print "===== auto-reloading ====="
    
def main():
    p = optparse.OptionParser()
    p.add_option('--port', '-p', default='5000',help='port diazo must run at')
    p.add_option('--content', '-c', default='http://localhost',help='format: http://<domain>')
    p.add_option('--rules', '-r', default='',help='Path of rules.xml')
    p.add_option('--static', '-s', default='',help='Path to static content')
    options = p.parse_args()[0]
    """
    "mapper" Is an object normally filled by the Mapper class from thememapper.core
    When starting thememapper.diazo standalone this object needs to be created.
    """
    mapper = {}
    mapper['diazo_port'] = options.port
    mapper['content_url'] = options.content
    mapper['rules_path']= options.rules
    mapper['static_path']= options.static
    start_diazo_server(Mapper(**mapper))

if __name__ == '__main__':
    main()
