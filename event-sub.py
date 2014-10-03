#!/usr/bin/env python

import os
import sys
import zmq

import logging
import json

from optparse import OptionParser
from multiprocessing import cpu_count

from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase
from eventreactor.eventhandlers import EventFilterManager, DriverManager

from pprint import pprint


log = logging.getLogger(__name__)


class EventSubscriber(object):

	log = logging.getLogger("%s.EventSubscriber" %(__name__))

	def __init__(self, uri, event_filters, event_handlers_dir=''):
		self.uri = uri
		self.zbase = ZBase(self.uri, "zmq.SUB")
		self.eventFilters = EventFilterManager(event_filters)
		self.eventHandlersDir = event_handlers_dir
		self.__driverMgr = DriverManager(self.eventHandlersDir)


	def __executeHandler(self, handler, event):
		#dm = DriverManager()
		return self.__driverMgr.execDriverHandler(
									handler['driver'], 
									handler['handler'], event)


	def runHandlers(self, handlers, data):
		for handler in handlers:
			if handler.get('exclusive'):
				self.log.warning("TODO: EXCLUSIVE handler: %s, data: %s" %(str(handler), str(data)))
			else:
				rslt = self.__executeHandler(handler, data)
				self.log.info("Result: %s" %(str(rslt)))


	def start(self, callback=None):
		self.zbase.connect()
		try:
			self.log.info("Waiting for events...")
			while True:
				dataStr = self.zbase.sock.recv()
				data = json.loads(dataStr)

				handlers = self.eventFilters.eventHandlers(data)
				self.log.info("event: %s, handlers: %s" %(data['event_type'], str(handlers)))
				self.runHandlers(handlers, data)

				if callback != None: callback(data)

		except KeyboardInterrupt:
			self.zbase.close()


def checkOptions():
	parser = OptionParser()
	parser.add_option("--event-handlers", 	   dest="eventHandlers", default="/etc/event-reactor/event-handlers",
			help="Directory containing event handlers")
	parser.add_option("-e", "--event-filters", dest="eventFilters",  default="/etc/event-reactor/event-handlers.json",
			help="Event filters config file")
	parser.add_option("-u", "--publisher-uri", dest="pubUri",        default="tcp://127.0.0.1:55000",
			help="URI of publisher to connect to")

	(opts, args) = parser.parse_args()

	if os.path.exists(opts.eventFilters):
		opts.eventFilters = json.load(open(opts.eventFilters))
	else:
		print "\n * Event filters config not found: %s\n" %(opts.eventFilters)
		sys.exit(1)

	return opts, args


def main():

	logging.basicConfig(level=logging.INFO, 
		format="%(asctime)s (%(process)d) [%(levelname)s %(lineno)s:%(name)s.%(funcName)s]: %(message)s")

	(opts, args) = checkOptions()

	esub = EventSubscriber(opts.pubUri, event_filters=opts.eventFilters, 
										event_handlers_dir=opts.eventHandlers)
	esub.start()


if __name__ == "__main__":
	main()
