#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SQLite( object ): # no, think twice before you do this...
						# if you still want to - think again

	@staticmethod
	def create():
		engine=create_engine('sqlite:///cms.db')
		Base.metadata.create_all(engine)
		return sessionmaker(bind=engine)()

class MySQL( object ):

	@staticmethod
	def create():
		creds = 'mysql+pymysql://root:root@localhost/enum_cms?charset=utf8'
		engine=create_engine( creds, pool_size=0xF, max_overflow=0 )
		Base.metadata.create_all(engine)
		return sessionmaker(bind=engine)()

class Session( object ):

	def __init__( self, session='default' ):
		self._session = session

	@property
	def session( self ):
		return self._session
