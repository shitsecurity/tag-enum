#!/usr/bin/env python

import exception

from shell import call, shell

try:
    call( 'git' )
except OSError:
    err_msg = "is git installed? make sure it's in $PATH."
    raise exception.MissingDependency(err_msg)

import os
import logging

from functools import wraps

class GitAPI( object ):

    @staticmethod
    def clone( repo ):
        call(['git' ,'clone', '{}'.format( repo )])

    @staticmethod
    def tags():
        return filter(None, shell(['git', 'tag']).split('\n'))

    @staticmethod
    def checkout( repo, tag='' ):
        shell(['git', 'checkout', '{}'.format( tag )])

    @staticmethod
    def pull():
        call(['git', 'pull'])

    @staticmethod
    def clean():
        call('rm -rf *', shell=True ) # XXX: nix only

def repo_chdir( f ):
    @wraps( f )
    def wrapper( self, repo, *args, **kwargs ):
        owd = os.getcwd()
        try:
            dir = repo.split('/')[-1]
            path = os.path.join( owd, dir )
            os.chdir( path )
            logging.debug( 'chdir to {}'.format( path ))
            result = f( self, repo, *args, **kwargs )
            os.chdir( owd )
            logging.debug( 'chdir to {}'.format( owd ))
            return result
        except OSError:
            logging.error( 'failed chdir to {}'.format( path ))
    return wrapper

def git_chdir( f ):
    @wraps( f )
    def wrapper( self, *args, **kwargs ):
        owd = os.getcwd()
        logging.debug( 'cwd is {}'.format( owd ))
        if not os.path.isdir( self.path ):
            logging.debug('creating dir {}'.format( self.path ))
            os.mkdir( self.path )
        os.chdir( self.path )
        result = f( self, *args, **kwargs )
        os.chdir(owd)
        return result
    return wrapper

class GitManager( object ):

    def __init__( self, config, dir ):
        self.repos = filter(lambda _: _.type=='git', config.repos)
        self.path = os.path.abspath(os.path.expanduser( dir ))

    def clone( self, repo ):
        logging.info( 'cloning repo {}'.format( repo ))
        GitAPI.clone( repo )

    @repo_chdir
    def tags( self, repo ):
        logging.debug( 'extracting tags from {}'.format( repo ))
        return GitAPI.tags()

    @repo_chdir
    def pull( self, repo ):
        logging.info( 'pulling repo {}'.format( repo ))
        GitAPI.pull()

    @git_chdir
    def setup( self ):
        logging.info( 'cloning repos to {}'.format( self.path ))
        map( self.clone, [ _.git for _ in self.repos ])

    @git_chdir
    def update( self ):
        map( self.pull, [ _.git for _ in self.repos ])

    @git_chdir
    def parse_tags( self ):
        tags = {}
        for repo in self.repos:
            tags[ repo.name ] = self.tags( repo.git )
        return tags

    @git_chdir
    def clean( self ):
        logging.debug( 'cleaning {}'.format( os.getcwd() ))
        GitAPI.clean()

    @git_chdir
    @repo_chdir
    def checkout( self, repo, tag ):
        logging.debug( 'checkout {} {}'.format( repo, tag ))
        GitAPI.checkout( repo, tag=tag )
