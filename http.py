#!/usr/bin/env python

from requests import Session as RequestsSession

class Session( RequestsSession ):

	UA = 'Mozilla/5.0'

	def __init__( self, *args, **kwargs ):
		super( Session, self ).__init__( *args, **kwargs )
		self.headers['User-Agent'] = Session.UA
