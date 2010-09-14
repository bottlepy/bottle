#!/usr/bin/python
# -*- coding: utf-8 -*-

__autor__   = "Damien Degois"
__version__ = '0.1'
__licence__ = 'MIT'

import bottle
import struct, time, zlib

class OtfCompressPlugin(bottle.BasePlugin):
    plugin_name = "otfcompress"

    def wrap(self, callback):
        def wrapper(*args, **kwargs):
            rv = ""
            try:
                rv = callback(*args, **kwargs)
                if bottle.request.headers.get("Accept-Encoding"):
                    # Split and cleanup accept-encoding header
                    # 'Accept-Encoding: deflate, gzip' => ['deflate', 'gzip']
                    spae = map(lambda x: x.strip(), bottle.request.headers.get("Accept-Encoding").split(','))
                    enc = ""
                    for e in spae:
                        # Might have gzip or x-gzip
                        if "gzip" in e:
                            enc = e
                    if enc:
                        bottle.response.headers['Content-Encoding'] = enc
                        if isinstance(rv ,bottle.HTTPResponse):
                            # Apply rv headers
                            rv.apply()
                            # but delete content-length header
                            # (not determinable without mapping all data in ram)
                            del(bottle.response.headers['Content-Length'])
                            return iter_compress(rv.output)
                        else:
                            return iter_compress(rv)
                    else:
                        return rv
                else:
                    return rv
            except Exception, e:
                #print str(e)
                return rv
        return wrapper

    
def write32u(value):
    return struct.pack("<L", value)

# From Gzip
def iter_compress(it, compresslevel=9):
    crc = zlib.crc32("") & 0xffffffffL
    compress = zlib.compressobj(compresslevel,
                                zlib.DEFLATED,
                                -zlib.MAX_WBITS,
                                zlib.DEF_MEM_LEVEL,
                                0)
    size = 0
    # header + method + flag (0) + time + misc headers
    yield '\037\213\010\000'+write32u(long(time.time()))+'\002\377'
    for e in it:
        size += len(e)
        crc = zlib.crc32(e, crc) & 0xffffffffL
        yield compress.compress(e)

    # Close
    yield compress.flush()
    yield write32u(crc) + write32u(size & 0xffffffffL)
    
