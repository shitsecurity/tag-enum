#!/usr/bin/env python

import os
import yaml
import logging

class SvnRepo(yaml.YAMLObject):
    yaml_tag = '!Svn'
    type = 'svn'

class GitRepo(yaml.YAMLObject):
    yaml_tag = '!Git'
    type = 'git'

    @property
    def dir( self ):
        return self.git.split('/')[-1]

class HashFile(yaml.YAMLObject):
    yaml_tag = '!File'

class HashExt(yaml.YAMLObject):
    yaml_tag = '!Extension'

    @property
    def ext( self ):
        return '.{}'.format( self.extension )

class Resources():

    def __init__( self, file='config.yaml' ):
        path = os.path.abspath(os.path.expanduser( file ))
        logging.debug('loading resources from {}'.format( path ))
        with open( path, 'rb' ) as fh:
            loader = yaml.load( fh )

        self.extensions = loader['extensions']
        self.files = loader['files']
        self.repos = loader['repos']

        self.db = loader['db']
