#!/usr/bin/env python

import subprocess

from functools import partial

call = partial( subprocess.call,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE )

shell = lambda _, *args, **kwargs: subprocess.Popen( _,
                                                    *args,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    **kwargs ).communicate()[0]
