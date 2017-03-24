#!/usr/bin/env python
# -*- coding: utf-8 -*-

USAGE = "./main.py <path to config file>\n"

if __name__ == "__main__":    
    import sys            
    from options import ServerOptions
    from server import Server    
    argv = sys.argv
     
    if len(argv) != 2:
        sys.stderr.write(USAGE)
        sys.exit(1)
    
    try:
        options = ServerOptions(argv[1])    
    except Exception as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)
        
    server = Server(options.server_port,
                    options.obsolete_time,
                    options.clean_period,
                    options.html_path,
                    options.css_path,
                    options.js_path)
    server.run()
