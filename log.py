#!/usr/bin/env python

import logging

def log( level=logging.DEBUG ):
	logging.getLogger('requests').setLevel( logging.ERROR )
	format='%(levelname)8s [*] %(message)s'
	logging.basicConfig(level=level,format=format)
