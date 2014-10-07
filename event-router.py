#!/usr/bin/env python

import logging
import os
import sys
import json
from optparse import OptionParser

from eventreactor.conf import loadConfig
from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase
from eventreactor.mqaggr.inputs import *

from pprint import pprint 


def loadInputFeeds(config):
	feeders = []
	for qi in config['feeders']:
		if qi.get('disabled'):
			continue
		feeder = eval("%s(config['aggregator'], namespace=qi['namespace'], config=qi['config'])" %(
																					qi['handler']))
		feeder.start()
		feeders.append(feeder)		
	return feeders


def checkOptions():
	parser = OptionParser()
	parser.add_option("-c", "--config", dest="config", default="/etc/event-reactor/config.json")
	(opts, args) = parser.parse_args()

	if os.path.exists(opts.config):
		opts.config = loadConfig(opts.config)
	else:
		print "\n * Could not find config: %s\n" %(opts.config)
		sys.exit(1)

	return (opts, args)


def main():
	(opts, args) = checkOptions()

	log = logging.getLogger(__name__)	
	logging.basicConfig(level=eval("logging.%s" %(opts.config['logging']['loglevel'])), 
												format=opts.config['logging']['format'])
	
	aggrConfig = opts.config['aggregator']['config']
	aggrServer = ZBase(aggrConfig['uri'], aggrConfig['type'])
	log.info("Listening on (%s): %s" %(aggrConfig['type'], aggrConfig['uri']))
	aggrServer.bind()
	
	pubSrvCfg = opts.config['outputs'][0]['config']
	pubServer = ZBase(pubSrvCfg['uri'], pubSrvCfg['type'])
	log.info("Listening on (%s): %s" %(pubSrvCfg['type'], pubSrvCfg['uri']))
	pubServer.bind()
	
	feeds = loadInputFeeds(opts.config['feeds'])
	log.info("Feeders loaded: %d" %(len(feeds)))
	try:
		## Feed data to publishing stream
		while True:
			
			rslt = aggrServer.sock.recv()
			try:
				resp = json.loads(rslt)
				log.info("Publishing: %(namespace)s:%(event_type)s" %(resp))
			
				pubServer.sock.send(rslt)

			except Exception,e:
				log.error("%s '%s'" %(str(e), str(rslt)))

	except KeyboardInterrupt:
		
		for feed in feeds:
			feed.shutdown()
			feed.terminate()

		#aggrServer.close()
		#pubServer.close()


if __name__ == "__main__":
	main()
