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


def loadInputFeeders(config):

	# localhost host should be the host the feeders connect to, to submit data
	aggrClientUri = "%(protocol)s://localhost:%(port)d" %(config['aggregator']['config'])
	feeders = []
	for qi in config['inputs']:
		feeder = eval("%s(outputUri=aggrClientUri, config=qi['config'])" %(
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
	
	feeders = loadInputFeeders(opts.config)
	log.info("Feeders loaded: %d" %(len(feeders)))
	try:
		## Feed data to publishing stream
		while True:

			rslt = aggrServer.sock.recv()
			resp = json.loads(rslt)
			log.info("Publishing: %(event_type)s" %(resp))
			
			pubServer.sock.send(rslt)

	except KeyboardInterrupt:
		
		for feeder in feeders:
			feeder.shutdown()
			feeder.terminate()

		#aggrServer.close()
		#pubServer.close()


if __name__ == "__main__":
	main()
