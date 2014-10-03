
import os
import json


def loadConfig(cfgfile):
	
	cfgdata = json.load(open(cfgfile))
	
	cfgdata['aggregator']['config']['uri'] = "%(protocol)s://%(listen_address)s:%(port)d" %(
															cfgdata['aggregator']['config'])

	for output in cfgdata['outputs']:
		output['config']['uri'] = "%(protocol)s://%(listen_address)s:%(port)d" %(
																output['config'])

	return cfgdata