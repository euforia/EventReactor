#!/usr/bin/env python
'''

Fire event to the zeromq REP/REQ topology

'''
import zmq
import sys
import logging
import json
from optparse import OptionParser

from eventreactor.clients import EventPusher

log = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s (%(process)d) [%(levelname)s %(lineno)s:%(name)s.%(funcName)s]: %(message)s"


def checkOptions():
	parser = OptionParser()
	parser.add_option("-p", "--payload", 	dest="payload")
	parser.add_option("-e", "--event-type", dest="eventType")
	parser.add_option("-n", "--namespace",  dest="namespace", default="local")
	parser.add_option("-u", "--uri", 		dest="uri", 	  default="tcp://127.0.0.1:55055")
	parser.add_option("-z", "--zmq-type", 	dest="zmqType",   default="zmq.REQ")
	(opts, args) = parser.parse_args()
	
	if not opts.eventType or not opts.payload:
		parser.print_help()
		sys.exit(1)

	if opts.payload.startswith("@"):
		opts.payload = json.loads(open(opts.payload[1:], "rb"))
	else:
		opts.payload = json.loads(opts.payload)

	return opts, args


def main():

	logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

	(opts, args) = checkOptions()	

	epusher = EventPusher(opts.uri)
	resp = epusher.pushEvent(opts.namespace, opts.eventType,  opts.payload)
	print resp

	epusher.zbase.close()


if __name__ == "__main__":
	main()
