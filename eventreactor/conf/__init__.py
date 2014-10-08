
import os
import json


def loadConfig(cfgfile):
	
	cfgdata = json.load(open(cfgfile))
	
	cfgdata['aggregator']['config']['uri'] = "%(protocol)s://%(listen_address)s:%(port)d" %(
															cfgdata['aggregator']['config'])

	for output in cfgdata['outputs']:
		output['config']['uri'] = "%(protocol)s://%(listen_address)s:%(port)d" %(
																output['config'])

	cfgdata['feeds']['aggregator']['uri'] = "%(protocol)s://%(host)s:%(port)d" %(
													cfgdata['feeds']['aggregator'])	
	
	
	if cfgdata.get('event_handlers_dir') == None:
		cfgdata['event_handlers_dir'] = os.path.join(os.path.dirname(os.path.dirname(
										os.path.abspath(__file__))), "etc/event-handlers")
		if not os.path.exists(cfgdata['event_handlers_dir']):
			cfgdata['event_handlers_dir'] = "/etc/event-reactor/event-handlers"

	return cfgdata
