#!/usr/bin/env python

import hashlib

def hash( data ):
    return hashlib.sha1( data ).hexdigest()

def hash_file( path ):
    with open( path, 'rb' ) as fh:
        data = ''.join(fh.readlines())
    return hash(data)
