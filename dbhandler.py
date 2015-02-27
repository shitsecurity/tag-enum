#!/usr/bin/env python

from db import Session, func, SQLite, MySQL
from models import Identifier

import logging

from functools import wraps

def ret( index=0, iter=False ):
	def decorator( f ):
		@wraps( f )
		def wrapper( *args, **kwargs ):
			return [ _[index] for _ in f( *args, **kwargs ) ]
		@wraps( f )
		def iwrapper( *args, **kwargs ):
			for result in f( *args, **kwargs ):
				yield result[index]
		if iter:
			return iwrapper
		else:
			return wrapper
	return decorator

def limit( amount=None ):
	def decorator( f ):
		@wraps( f )
		def wrapper( *args, **kwargs ):
			limit = kwargs.pop('limit',amount)
			result = f( *args, **kwargs )
			if limit is not None: result = result.limit( limit )
			return result
		return wrapper
	return decorator

def offset( amount=None ):
	def decorator( f ):
		@wraps( f )
		def wrapper( *args, **kwargs ):
			offset = kwargs.pop('offset',amount)
			result = f( *args, **kwargs )
			if offset is not None: result = result.offset( offset )
			return result
		return wrapper
	return decorator

def batch( amount=0x10 ):
	def decorator( f ):
		@wraps( f )
		def wrapper( *args, **kwargs ):
			return f( *args, **kwargs ).yield_per( amount )
		return wrapper
	return decorator

class Handler( Session ):
	LAZY_CACHE = 0x1000

	def __init__( self ):
		self._lazy_save_obj = []
		self._lazy_counter = 0
		#self.db = SQLite.create() # XXX
		self.db = MySQL.create()

	def lazy_save( self, obj ):
		logging.debug( 'lazy save {}'.format( obj ))
		self._lazy_save_obj.append( obj )
		self._lazy_counter += 1
		if self._lazy_counter > self.LAZY_CACHE:
			self.flush_lazy()

	def flush_lazy( self ):
		logging.debug( 'flushing {} objects'.format( len(self._lazy_save_obj) ))
		for obj in self._lazy_save_obj:
			self.db.add( obj )
		self.db.commit()
		self._lazy_save_obj = []
		self._lazy_counter = 0

	def reset( self ):
		logging.debug( 'reset: deleting records' )
		#Identifier.__table__.drop(self.engine)
		self.db.query(Identifier).delete()
		self.db.commit()

	def _cms( self ):
		'''
		select distinct cms from identifier;
		'''
		return self.db.query( Identifier.cms ).distinct()

	@ret(0)
	def cms( self ):
		return self._cms().all()

	def cms_count( self ):
		return self._cms().count()

	def _tags( self, cms=None ):
		'''
		select distinct tag from identifier where cms='{CMS}';
		'''
		query = self.db .query( Identifier.tag )
		if cms: query = query.filter( Identifier.cms==cms )
		return query.distinct()

	@ret(0)
	def tags( self, *args, **kwargs ):
		return self._tags( *args, **kwargs ).all()

	def tag_count( self, *args, **kwargs ):
		return self._tags( *args, **kwargs ).count()

	@limit()
	@offset()
	def _query_next( self, cms=None, tags=None ):
		'''
		select url,tag,hash,count(hash) as x from identifier
		where cms='{CMS}' and tag in 
		( select distinct( tag ) from identifier where cms='{CMS}')
		group by hash order by x asc;
		'''
		query = self.db .query( Identifier )
		if cms: query = query.filter( Identifier.cms==cms )
		if tags: query = query.filter( Identifier.tag.in_(tags) )
		query = query   .group_by( Identifier.hash ) \
						.order_by( func.count(Identifier.hash).asc() )
		return query
	
	def query_next( self, *args, **kwargs ):
		return self._query_next( *args, **kwargs ).first()

	def query_all( self, *args, **kwargs ):
		return self._query_next( *args, **kwargs ).all()

	def _tags_via_hash( self, hash, cms=None ):
		'''
		select distinct tag from identifier where cms='{CMS}' and hash='{HASH}';
		'''
		query = self.db .query( Identifier.tag )
		if cms: query = query.filter( Identifier.cms==cms )
		return query.filter( Identifier.hash==hash )
	
	@ret(0)
	def tags_via_hash( self, *args, **kwargs ):
		return self._tags_via_hash( *args, **kwargs ).all()

	def _tags_via_url( self, url, cms=None ):
		'''
		select distinct tag from identifier where cms='{CMS}' and url='{URL}';
		'''
		query = self.db .query( Identifier.tag )
		if cms: query = query.filter( Identifier.cms==cms )
		return query.filter( Identifier.url==url )
	
	@ret(0)
	def tags_via_url( self, *args, **kwargs ):
		return self._tags_via_url( *args, **kwargs ).all()
