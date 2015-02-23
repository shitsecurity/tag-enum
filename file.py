#!/usr/bin/env python

import os.path

from collections import namedtuple

Match = namedtuple('File',['name','url','path',])

class Finder( object ):
	
	def __init__( self, config, dir ):
		self.files = config.files
		self.ext = config.extensions
		self.path = os.path.abspath(os.path.expanduser( dir ))

	def find( self, repo ):
		compute_path = lambda _: os.path.realpath( os.path.join( *_ ))
		repo_path = compute_path([ self.path, '.{}'.format(repo.root), repo.dir ])
		for (path, dirs, files) in os.walk( repo_path ):
			for file in files:
				if self.match( file ):
					webroot_path = path[len(repo_path):]
					file_path = os.path.join( path, file )
					url = '{}/{}'.format( webroot_path, file )
					yield Match( name=file, path=file_path, url=url )

	def match( self, file ):
		if any([file.endswith(_.ext) for _ in self.ext ]):
			return True

		if any([file==_.name for _ in self.files]):
			return True
