import threading
import uuid 
import datetime
class StorageItem(object): 
    __slots__ = [ 'last_operation', 'parser' ]
    def __init__(self, parser):
        self.last_operation = datetime.datetime.now()
        self.parser = parser
    
    def update_time(self):
        self.last_operation = datetime.datetime.now()
        
class Storage(object):
    def __init__(self, thread_safe=False):        
        self.parser_dict = {}        
        self.thread_safe = thread_safe
        self.lock = threading.Lock() if self.thread_safe else None
        
    def _acquire(self):
        if self.thread_safe:
            self.lock.acquire()
            
    def _release(self):
        if self.thread_safe:
            self.lock.release()
            
    def _generate_id(self):        
        while True:
            id = str(uuid.uuid4())
            if id not in self.parser_dict:
                return id
                
    def add(self, parser):
        self._acquire()
        id = self._generate_id()
        self.parser_dict[id] = StorageItem(parser)
        self._release()
        return id
        
    def get(self, id, ttl):
        self._acquire()
        current = datetime.datetime.now()
        value = None
        
        if id in self.parser_dict:
            item = self.parser_dict[id]
            if (current - item.last_operation).total_seconds() <= ttl:
                value = item.parser
                item.update_time()
            
        self._release()
        return value
        
    def clean_old(self, ttl):
        self._acquire()
        
        current = datetime.datetime.now()
        items = self.parser_dict.items()        
        old_items = filter(lambda x: (current - x[1].last_operation).total_seconds() > ttl, items)
        old_ids = map(lambda x: x[0], old_items)
        for iter_id in old_ids:
            del self.parser_dict[iter_id]
            
        self._release()
    
    def delete(self, id):
        self._acquire()
        
        if id in self.parser_dict:
            del self.parser_dict[id]
            
        self._release()
