
import json
import logging

from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase
from eventreactor.eventhandlers import EventFilterManager, DriverManager

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