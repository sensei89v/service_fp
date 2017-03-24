# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import os 
import json
from storage import Storage
from parser import build_parser, PARSER_COUNTER

class ServerHandler(tornado.web.RequestHandler):
    def initialize(self, server_ctx):
        self.server_ctx = server_ctx        
        
class MainHandler(ServerHandler):      
    HTML_PAGE = "main.html"
    
    def get(self):        
        page = self.server_ctx.get_html_page(self.HTML_PAGE)
        self.write(page)        

# TODO: может CSSHandler и JSHandler лучше объединить в один
class CSSHandler(ServerHandler):      
    def get(self):                        
        page = self.server_ctx.get_css_page(self.request.path)        
        if page is None: 
            self.send_error(404, reason="not found")
        else:
            self.write(page)        

class JSHandler(ServerHandler):      
    def get(self):                    
        page = self.server_ctx.get_js_page(self.request.path)        
        if page is None: 
            self.send_error(404, reason="not found")
        else:
            self.write(page)        


class StartSendHandler(ServerHandler):
    def post(self):    
        parser = build_parser(PARSER_COUNTER)        
        id = self.server_ctx.storage.add(parser)           
        response = json.dumps({"id": id})          
        self.set_header('Content-Type', 'application/json')   
        self.write(response)
 
class UploadHandler(ServerHandler):
    def post(self):      
        if 'uid' not in self.request.headers:
            self.send_error(500, reason='Uid is missing')
            return 
            
        uid = self.request.headers['uid']
        parser = self.server_ctx.get_parser(uid)
        if parser is None:
            self.send_error(500, reason='unknown UID')
            return             
             
        parser.parse(self.request.body)        

class FinishSendHandler(ServerHandler):
    def post(self):        
        if 'uid' not in self.request.headers:
            self.send_error(500, 'Uid is missing')
            return 
            
        uid = self.request.headers['uid']
        parser = self.server_ctx.get_parser(uid)
        
        if parser is None:
            self.send_error(500, 'unknown UID')
            return 
        result = parser.finish()     
        self.set_header('Content-Type', 'application/json')       
        self.write(result)
        self.server_ctx.delete_parser(uid)

class RestoreHandler(ServerHandler):
    def get(self):
        if 'uid' not in self.request.headers:
            self.send_error(500, reason='Uid is missing')
            return 
            
        uid = self.request.headers['uid']
        parser = self.server_ctx.get_parser(uid)
        
        if parser is None:
            self.write(json.dumps({ "pos": None }))
        else:
            self.write(json.dumps({ "pos": parser.get_pos() }))            
        
class Server(object):    
    #TODO: может лучше передавать сразу объектом?
    def __init__(self, server_port, obsolete_time, clean_period, 
                 html_path, css_path, js_path):
        self.server_port = server_port
        self.obsolete_time = obsolete_time
        self.clean_period = clean_period
        self.html_path = html_path
        self.css_path = css_path        
        self.js_path = js_path
        self.storage = Storage(False)
        self.server = tornado.web.Application([(r"/", MainHandler, dict(server_ctx=self)),
                                               (r"/start_send", StartSendHandler, dict(server_ctx=self)),
                                               (r"/upload", UploadHandler, dict(server_ctx=self)), 
                                               (r"/finish_send", FinishSendHandler, dict(server_ctx=self)),
                                               (r"/restore", RestoreHandler, dict(server_ctx=self)),
                                               (r"/.*\.css$", CSSHandler, dict(server_ctx=self)),
                                               (r"/.*\.js$", JSHandler, dict(server_ctx=self))])   
    def get_html_page(self, page):
        return self.get_page(self.html_path, page)
        
    def get_css_page(self, page):        
        return self.get_page(self.css_path, page)
        
    def get_js_page(self, page):
        return self.get_page(self.js_path, page)
        
    def get_page(self, prefix, page):
        while page.startswith("/"):
            page = page[1:]
             
        path = os.path.join(prefix, page)
        
        if not os.path.exists(path):
            return None
            
        fi = open(path)
        web_page = fi.read()
        fi.close()
        return web_page
    
    def get_parser(self, uid):
        return self.storage.get(uid, self.obsolete_time)
    
    def delete_parser(self, uid):
        return self.storage.delete(uid)
    
    def clean_callback(self):              
        self.storage.clean_old(self.obsolete_time)
        
    def run(self):
        loop = tornado.ioloop.IOLoop.instance()  
        pereodic = tornado.ioloop.PeriodicCallback(self.clean_callback, self.clean_period * 1000, io_loop=loop)
        pereodic.start()             
        self.server.listen(self.server_port)
        loop.start()       
