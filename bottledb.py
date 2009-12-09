DB_PATH = './'

class BottleBucket(object): # pragma: no cover
    """ Memory-caching wrapper around anydbm """
    def __init__(self, name):
        self.__dict__['name'] = name
        self.__dict__['db'] = dbm.open(DB_PATH + '/%s.db' % name, 'c')
        self.__dict__['mmap'] = {}
            
    def __getitem__(self, key):
        if key not in self.mmap:
            self.mmap[key] = pickle.loads(self.db[key])
        return self.mmap[key]
    
    def __setitem__(self, key, value):
        if not isinstance(key, str): raise TypeError("Bottle keys must be strings")
        self.mmap[key] = value
    
    def __delitem__(self, key):
        if key in self.mmap:
            del self.mmap[key]
        del self.db[key]

    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try: del self[key]
        except KeyError: raise AttributeError(key)

    def __iter__(self):
        return iter(self.ukeys())
    
    def __contains__(self, key):
        return key in self.ukeys()
  
    def __len__(self):
        return len(self.ukeys())

    def keys(self):
        return list(self.ukeys())

    def ukeys(self):
      return set(self.db.keys()) | set(self.mmap.keys())

    def save(self):
        self.close()
        self.__init__(self.name)
    
    def close(self):
        for key in self.mmap:
            pvalue = pickle.dumps(self.mmap[key], pickle.HIGHEST_PROTOCOL)
            if key not in self.db or pvalue != self.db[key]:
                self.db[key] = pvalue
        self.mmap.clear()
        if hasattr(self.db, 'sync'):
            self.db.sync()
        if hasattr(self.db, 'close'):
            self.db.close()
        
    def clear(self):
        for key in self.db:
            del self.db[key]
        self.mmap.clear()
        
    def update(self, other):
        self.mmap.update(other)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            if default:
                return default
            raise


class BottleDB(threading.local): # pragma: no cover
    """ Holds multible BottleBucket instances in a thread-local way. """
    def __init__(self):
        self.__dict__['open'] = {}
        
    def __getitem__(self, key):
        warnings.warn("Please do not use bottle.db anymore. This feature is deprecated. You may use anydb directly.", DeprecationWarning)
        if key not in self.open and not key.startswith('_'):
            self.open[key] = BottleBucket(key)
        return self.open[key]

    def __setitem__(self, key, value):
        if isinstance(value, BottleBucket):
            self.open[key] = value
        elif hasattr(value, 'items'):
            if key not in self.open:
                self.open[key] = BottleBucket(key)
            self.open[key].clear()
            for k, v in value.iteritems():
                self.open[key][k] = v
        else:
            raise ValueError("Only dicts and BottleBuckets are allowed.")

    def __delitem__(self, key):
        if key not in self.open:
            self.open[key].clear()
            self.open[key].save()
            del self.open[key]

    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try: del self[key]
        except KeyError: raise AttributeError(key)

    def save(self):
        self.close()
        self.__init__()
    
    def close(self):
        for db in self.open:
            self.open[db].close()
        self.open.clear()

db = BottleDB()
