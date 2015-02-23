#!/usr/bin/env python

from db import Base
from sqlalchemy import Column
from sqlalchemy import Integer, String, Unicode

class Identifier( Base ):

	__tablename__ = 'identifier'

	id = Column( Integer, primary_key=True )

	#cms = Column( String )
	#tag = Column( String ) # version
	#url = Column( String ) # path relative to web root
	#path = Column( String ) # path relative to git root
	#name = Column( String ) # file name
	#hash = Column( String )

	cms = Column( String(16), index=True )
	tag = Column( String(32), index=True ) # version
	url = Column( String(128), index=True ) # path relative to web root
	path = Column( String(256) ) # path relative to git root
	name = Column( String(32) ) # file name
	hash = Column( String(40), index=True )

	def __repr__ ( self ):
		return "<{} {} {}>".format( self.cms, self.name, self.tag )
