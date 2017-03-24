# -*- coding: utf-8 -*-
import os
import json 

CONFIG_FIELD_SERVER_PORT = "server_port"
CONFIG_FIELD_OBSOLETE_TIME = "obsolete_time"
CONFIG_FIELD_CLEAN_PERIOD = "clean_period"
CONFIG_FIELD_HTML = "html"
CONFIG_FIELD_CSS = "css"
CONFIG_FIELD_JS = "js"
def _check_port(port):
    return (port > 0) and (port < 2**16)

def _check_int_positive(value):
    return value > 0

def _extract_field(config_obj, field, type_field, check_fn=None, convert_fn=None):
    value = None
    
    if field not in config_obj:
        raise ValueError("There isn't '%s' field" % field)
    
    value = config_obj[field]
    
    if not isinstance(value, type_field):
        raise ValueError("Invalid '%s' field" % field)
        
    if check_fn is not None and not check_fn(value):
        raise ValueError("Invalid '%s' field" % field)
    
    if convert_fn is not None:
        value = convert_fn(value)
        
    return value

class ServerOptions(object):    
    def __init__(self, config_path):
        self.server_port = None 
        self.obsolete_time = None 
        self.clean_period = None 
        self.html_path = None 
        self.css_path = None 
        self.js_path = None 
        
        if not os.path.exists(config_path):
            raise ValueError("Config file not found")
        
        config_obj = None 
        fi = open(config_path, "rt")
                
        try:            
            config_obj = json.load(fi)        
            fi.close()
        except:
            raise ValueError("Invalid config")
            
        self.parse_config(config_obj)
        
    def parse_config(self, config_obj):
        self.server_port = _extract_field(config_obj, CONFIG_FIELD_SERVER_PORT, int, _check_port)
        self.obsolete_time = _extract_field(config_obj, CONFIG_FIELD_OBSOLETE_TIME, int, _check_int_positive) 
        self.clean_period = _extract_field(config_obj, CONFIG_FIELD_CLEAN_PERIOD, int, _check_int_positive) 
        self.html_path = _extract_field(config_obj, CONFIG_FIELD_HTML, unicode, os.path.exists, os.path.abspath) 
        self.css_path = _extract_field(config_obj, CONFIG_FIELD_CSS, unicode, os.path.exists, os.path.abspath) 
        self.js_path = _extract_field(config_obj, CONFIG_FIELD_JS, unicode, os.path.exists, os.path.abspath) 
