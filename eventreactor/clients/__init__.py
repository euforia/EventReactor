
import json
import logging

from celery import Celery

from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase
from eventreactor.eventhandlers import EventFilterManager


CELERY_EVENT_HANDLER_FUNC = "eventworker.tasks.executeEventHandler"
CELERY_CONFIG_MODULE = "eventworker.celeryconfig"
CELERY_APP_NAME = "eventworker"


class EventPusher(object):

	log = logging.getLogger("%s.EventPusher" %(__name__))

	def __init__(self, uri="tcp://127.0.0.1:55055"):
		self.zmqType = "zmq.REQ"
		self.uri = uri
		self.zbase = ZBase(self.uri, self.zmqType)
		self.zbase.connect()

	def pushEvent(self, namespace, event_type, payload, parent_event=None):
		'''
			namespace    : namespace the event belongs to
			event_type   : event type e.g. zmq.test
			payload 	 : json serializeable datastructure
			parent_event : name of event firing this event (if any)
		'''
		data = {
			'namespace' : namespace,
			'event_type': event_type, 
			'payload'   : payload
		}
		if parent_event != None: data['parent_event'] = parent_event

		return self._pushEvent(data)

	def _pushEvent(self, event):
		self.zbase.send(event)
		rslt = self.zbase.sock.recv()
		return json.loads(rslt)	

	def close(self):
		self.zbase.close()


class EventSubscriber(object):

	log = logging.getLogger("%s.EventSubscriber" %(__name__))

	def __init__(self, uri, event_filters):
		self.uri = uri
		self.zbase = ZBase(self.uri, "zmq.SUB")
		self.eventFilters = EventFilterManager(event_filters)

		self.__celery = Celery(CELERY_APP_NAME)
		self.__celery.config_from_object(CELERY_CONFIG_MODULE)


	def runHandlers(self, handlers, data):
		for handler in handlers:
			self.log.info("Submitting task: %s" % data)
			self.__celery.send_task(CELERY_EVENT_HANDLER_FUNC, (handler, data))

	def start(self, callback=None):
		self.zbase.connect()
		try:
			self.log.info("Waiting for events...")
			while True:
				dataStr = self.zbase.sock.recv()
				data = json.loads(dataStr)

				handlers = self.eventFilters.eventHandlers(data)
				self.log.info("namespace: %s, event: %s, handlers: %s" %(
					data['namespace'], data['event_type'], str(handlers)))
				
				self.runHandlers(handlers, data)

				if callback != None: callback(data)

		except KeyboardInterrupt:
			self.zbase.close()
