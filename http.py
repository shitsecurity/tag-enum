#!/usr/bin/env python

import requests.packages
requests.packages.urllib3.disable_warnings()

from requests import Session as RequestsSession

class Session( RequestsSession ):

    UA = 'Mozilla/5.0'

    def __init__( self, *args, **kwargs ):
        super( Session, self ).__init__( *args, **kwargs )
        self.headers['User-Agent'] = Session.UA
