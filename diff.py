#!/usr/bin/env/python

from functools import partial 

from difflib import SequenceMatcher as Differ
Diff = partial( Differ, None )
