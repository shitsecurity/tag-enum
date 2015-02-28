#!/usr/bin/env python

import argparse
import git
import log
import logging
import resource
import sys
import file
import os
import hash
import models
import dbhandler
import http
import diff
import random
import string

def parse_args():
	description = 'enumerate cms versions via dcvs tags'
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('--verbose', action='store_true', dest='verbose',
						help='be verbose' )
	parser.add_argument('--setup', action='store_true', dest='setup',
						help='clone repos' )
	parser.add_argument('--update', action='store_true', dest='update',
						help='update repos' )
	parser.add_argument('--parse', action='store_true', dest='parse',
						help='parse repos' )
	parser.add_argument('--config',metavar='config.yaml',dest='config',type=str,
						help='yaml configuration file', default='config.yaml' )
	parser.add_argument('--target', metavar='sub.domain.tld', dest='target',
						type=str, help='base url' )
	parser.add_argument('--delete', action='store_true', dest='delete',
						help='delete repos' )
	parser.add_argument('--identify', action='store_true', dest='identify',
						help='identify cms version' )
	parser.add_argument('--list', action='store_true', dest='list',
						help='list cms' )
	parser.add_argument('--cms', metavar='cms', dest='cms', type=str,
						help='target cms', default=None )
	parser.add_argument('--diff', metavar='404_NOT_FOUND', dest='diff',
						type=str, help='custom 404 path' )
	parser.add_argument('--ratio', metavar='0.95', dest='ratio',
						type=float, help='diff ratio', default=0.95 )
	parser.add_argument('--summary', action='store_true', dest='summary',
						help='request summary' )
	args = parser.parse_args()

	if args.identify and args.target is None:
		parser.error('select cms')

	if( not args.setup
		and not args.update
		and not args.parse
		and not args.identify
		and not args.delete
		and not args.list ):
		parser.error('select action')

	return args

def setup( config, dir='repos' ):
	git.GitManager(config,dir).setup()

def update( config, dir='repos' ):
	git.GitManager(config,dir).update()

def list_cms( config ):
	for repo in config.repos:
		print ' [+] {}'.format( repo.name )
	sys.exit()

def delete( config, dir='repos' ):
	print '[!] delete everything in {} ?'.format( os.path.join( os.getcwd(), 
																dir ))
	answ = raw_input( '[y|N] > ' )
	if answ.lower().strip() == 'y':
		git.GitManager(config,dir).clean()
	else:
		print '[*] rm -rf / &' # ha, ha-ha!
	sys.exit()

def parse( config, dir='repos', *args, **kwargs ):
	dbh = dbhandler.Handler()
	dbh.reset()
	finder = file.Finder(config,dir)
	git_manager = git.GitManager(config,dir)
	tags = git_manager.parse_tags( *args, **kwargs )
	for repo in config.repos:
		logging.info( 'parsing repo {}'.format( repo.name ))
		for tag in tags[ repo.name ]:
			logging.info( 'parsing tag {}'.format( tag ))
			git_manager.checkout( repo.git, tag )
			for match in finder.find(repo):
				id = models.Identifier( cms=repo.name,
										tag=tag,
										hash=hash.hash_file(match.path),
										name = match.name,
										url=match.url,
										path=match.path )
				dbh.lazy_save( id )
	dbh.flush_lazy()

def identify( config, target, cms, ratio=0.95, diff404=None, summary=False ):
	base_url=target.rstrip('/')
	if not base_url.startswith('http'): base_url = 'http://{}'.format(base_url)

	dbh = dbhandler.Handler()
	sess = http.Session()

	tags = dbh.tags(cms=cms)
	total = len(tags)
	requests = 0
	prev_response_tags = []

	rand_str = lambda: ''.join([random.choice(string.letters) for _ in
								xrange(random.randrange(8,17)) ])
	not_found = sess.get(base_url + '/' + (diff404 or rand_str()), verify=False)
	not_found_code = not_found.status_code
	not_found_data = not_found.content
	not_found_ratio = lambda _: diff.Diff( not_found_data, _ ).ratio()

	response_tags = None
	offset = 0

	while True:
		id = dbh.query_next( cms=cms, tags=tags, offset=offset )
		logging.debug( 'requesting {}'.format( id.url ))

		response = sess.get(base_url+id.url)
		requests += 1
		code = response.status_code
		data = response.content
		url = response.url
		file = id.url

		whitespace =  string.whitespace.replace(' ','')
		printable = lambda data: ''.join([ _ for _ in data
										if _ not in whitespace ])
		logging.debug('response: {} {}'.format(code,printable(data)[:66]))

		if code in [500,502,503]:
			logging.critical('server down')
			break
		elif code==404 or ( code==not_found_code
							and not_found_ratio(data)>=ratio ):
			logging.warning('{} not found {}'.format( code, url ))
			response_tags = dbh.tags_via_url( cms=cms, url=file )
			tags = list(set(tags).difference(response_tags))
		elif code==200:
			response_hash = hash.hash( response.content )
			logging.debug('{} {}'.format( url, response_hash ))
			response_tags = dbh.tags_via_hash( cms=cms, hash=response_hash )
			tags = list(set(tags).intersection(response_tags))
		elif code==403:
			logging.warning('{} access denied {}'.format( code, url ))
			offset += 1
		else:
			logging.critical('unrecognized http status code {}'.format(code))
			break

		if code!=403: offset = 0

		if prev_response_tags==response_tags:
			logging.info('duplicates detected')
			for tag in tags:
				logging.info('{}'.format(tag))
			break
		prev_response_tags=response_tags

		if len(tags)==1:
			logging.info('match {}'.format(tags[0]))
			break

	if summary:
		logging.info('{} cms versions exist'.format( total ))
		logging.info('{} cms versions detected'.format( len(tags) ))
		logging.info('{} requests sent'.format( requests ))

if __name__ == "__main__":
	args = parse_args()
	if args.verbose:
		level = logging.DEBUG
	else:
		level = logging.INFO
	log.log(level)
	rsrc = resource.Resources( args.config )
	if args.list: list_cms( rsrc )
	if args.delete: delete( rsrc )
	if args.setup: setup( rsrc )
	if args.update: update( rsrc )
	if args.parse: parse( rsrc )
	if args.identify: identify( rsrc,
								target=args.target,
								cms=args.cms,
								ratio=args.ratio,
								diff404=args.diff,
								summary=args.summary )
