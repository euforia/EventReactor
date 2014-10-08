#!/usr/bin/env python

import os
import sys
import logging
import json
from optparse import OptionParser

from eventreactor.clients import EventSubscriber

from pprint import pprint

logFormat = "%(asctime)s (%(process)d) [%(levelname)s %(lineno)s:%(name)s.%(funcName)s]: %(message)s"
log = logging.getLogger(__name__)


def checkOptions():
	parser = OptionParser()
	parser.add_option("--event-handlers", 	   dest="eventHandlers", default="/etc/event-reactor/event-handlers",
			help="Directory containing event handlers")
	parser.add_option("-e", "--event-filters", dest="eventFilters",  default="/etc/event-reactor/event-handlers.json",
			help="Event filters config file")
	parser.add_option("-u", "--publisher-uri", dest="pubUri",        default="tcp://127.0.0.1:55000",
			help="URI of publisher to connect to")
	parser.add_option("-l", "--log-level", 	   dest="logLevel",      default="INFO")

	(opts, args) = parser.parse_args()

	if os.path.exists(opts.eventFilters):
		opts.eventFilters = json.load(open(opts.eventFilters))
	else:
		print "\n * Event filters config not found: %s\n" %(opts.eventFilters)
		sys.exit(1)

	return opts, args


def main():

	(opts, args) = checkOptions()

	logging.basicConfig(
				level=eval("logging.%s" %(opts.logLevel)), 
				format=logFormat)

	esub = EventSubscriber(
				uri=opts.pubUri, 
				event_filters=opts.eventFilters)
	esub.start()


if __name__ == "__main__":
	main()
