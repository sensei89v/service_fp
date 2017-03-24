# -*- coding: utf-8 -*-
import json 

class AbsParser(object):  
    PARSER_NAME = 'abstract'  
    def __init__(self):
        self.pos = 0        
        
    def parse(self, data):
        self.pos += len(data)
    
    def calculate(self):
        return None 
        
    def finish(self):
        return json.dumps({
                            'parser': self.PARSER_NAME,                      
                            'result': self.calculate()
                          })
        
    def get_pos(self):
        return self.pos
            
class CounterParser(AbsParser):
    PARSER_NAME = 'counter'
    def __init__(self):
        super(CounterParser, self).__init__()
        self.count_table = [ 0 for i in xrange(0, 256)]        
        
    def parse(self, data):
        for iter in data:
            self.count_table[ord(iter)] += 1
        
        super(CounterParser, self).parse(data)
        
    def calculate(self):        
        items = map(lambda x: (x, self.count_table[x]), xrange(0, len(self.count_table)))        
        max_value = max(self.count_table)
        
        if max_value == 0: # Empty file
            return []            
        
        filtered_items = filter(lambda x: x[1] == max_value, items)        
        return map(lambda x: x[0], filtered_items)    

PARSER_COUNTER = 0

def build_parser(id):
    if id == PARSER_COUNTER:
        return CounterParser()
    
    return None
