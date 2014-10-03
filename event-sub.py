#!/usr/bin/env python

import os
import sys
import zmq

import logging
import json

from optparse import OptionParser
from multiprocessing import Pool, cpu_count

from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase
from eventreactor.eventhandlers import EventFilterManager, DriverManager

from pprint import pprint

FILTERS_CFGFILE = "etc/event-handlers.json"

log = logging.getLogger(__name__)


class EventSubscriber(object):

	log = logging.getLogger("%s.EventSubscriber" %(__name__))

	def __init__(self, uri, event_filters):
		self.uri = uri
		self.zbase = ZBase(self.uri, "zmq.SUB")
		self.eventFilters = EventFilterManager(event_filters)


	def __executeHandler(self, handler, event):
		dm = DriverManager()
		return dm.execDriverHandler(handler['driver'], 
								handler['handler'], event)


	def __runHandlers(self, handlers, data):
		for handler in handlers:
			if handler.get('exclusive'):
				#pool.apply_async(self.__executeHandler, handler, data, exclusiveCallback)
				self.log.info("TODO: exclusive handler: %s, data: %s" %(str(handler), str(data)))
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
				self.__runHandlers(handlers, data)

				if callback != None: callback(data)

		except KeyboardInterrupt:
			self.zbase.close()

'''
def getWorkerPool():
	workers = cpu_count()-1
	if workers == 0: workers = 1
	return Pool(workers)
'''
def checkOptions():
	parser = OptionParser()
	parser.add_option("-e", "--event-filters", dest="eventFilters", default="etc/event-handlers.json",
			help="Event filters config file")
	parser.add_option("-u", "--publisher-uri", dest="pubUri", default="tcp://127.0.0.1:55000",
			help="URI of publisher to connect to")

	(opts, args) = parser.parse_args()

	if not os.path.exists(opts.eventFilters):
		log.error("File not found: %s" %(opts.eventFilters))
		sys.exit(1)

	return opts, args


def main():

	logging.basicConfig(level=logging.INFO, 
		format="%(asctime)s (%(process)d) [%(levelname)s %(lineno)s:%(name)s.%(funcName)s]: %(message)s")

	(opts, args) = checkOptions()

	#workerPool = getWorkerPool()
	#log.info("Workers: %d" %(workerPool._processes))

	esub = EventSubscriber(opts.pubUri, event_filters=opts.eventFilters)
	esub.start()

	#workerPool.close()
	#workPool.join()
	#workPool.terminate()



if __name__ == "__main__":
	main()
