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
    
def init(settings):
    global http_host
    global server_name
    if settings['rules_path'] != '':
        if settings['diazo_port'] != '' and settings['content_url'] != '':
            http_host = urlparse(settings['content_url']).netloc
            server_name = socket.gethostbyname(http_host)
        else:
            raise Exception("Error: arguments can't be empty.")
    else:
        raise Exception("Error: You should specify a rules file.")
    if settings['static_path'] == '':
        settings['static_path'] = settings['theme_path']
    return settings

        
def get_application(settings):
    try:
        settings = init(settings)
        app = Flask(__name__)
        app.wsgi_app = DiazoMiddleware(MyWSGIProxyApp(settings['content_url']),None,settings['rules_path'],prefix='/thememapper_static',read_network=True,update_content_length=True,debug=True)
        handlers = [
            (r'/thememapper_static/(.*)', StaticFileHandler, {'path': settings['static_path']}),
            (r'/(.*)', FallbackHandler, {'fallback': WSGIContainer(app)})
            ]
        return Application(handlers)
    except Exception as e:
        print e
        return False
        
def start_diazo_server(settings):
    app = get_application(settings)
    if app is not False:
        print "Starting diazo on http://0.0.0.0:" + settings['diazo_port']
        HTTPServer(app).listen(settings['diazo_port'])
        ioloop = IOLoop.instance()
        autoreload.add_reload_hook(reload)
        autoreload.start(ioloop)
        ioloop.start()
        
def reload():
    print "===== auto-reloading ====="
    
def main():
    import os
    p = optparse.OptionParser()
    p.add_option('--port', '-p', default='5000',help='port diazo must run at')
    p.add_option('--content', '-c', default='http://localhost',help='format: http://<domain>')
    p.add_option('--rules', '-r', default='',help='Path of rules.xml')
    p.add_option('--static', '-s', default='',help='Path to static content')
    options = p.parse_args()[0]
    """
    "settings" Is a dict normally filled by the settings dict from thememapper.core
    When starting thememapper.diazo standalone this dict needs to be created.
    """
    settings = {}
    settings['diazo_port'] = options.port
    settings['content_url'] = options.content
    settings['rules_path']= options.rules
    if options.static == '':
        settings['static_path'] = os.path.dirname(settings['rules_path'])
    else:
        settings['static_path']= options.static
    start_diazo_server(settings)

if __name__ == '__main__':
    main()