
import time
import logging
import json

from multiprocessing import Process, Event

from eventreactor.mqaggr.wrappers.rmqwrappers import RabbitMQConsumer
from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase

from pprint import pprint


class BaseInput(Process):

	def __init__(self, aggr_config, namespace="local", config={}):
		super(BaseInput, self).__init__(group=None, target=None, name=None, args=(), kwargs={})

		self.namespace = namespace
		self.config = config

		self.outputUri = aggr_config['uri']
		self.outputType = aggr_config['type']


	def connectAggregator(self):
		zbase = ZBase(uri=self.outputUri, zmqType=self.outputType)
		zbase.connect()
		return zbase


class AMQPInput(BaseInput):

	log = logging.getLogger("%s.AMQPInput" %(__name__))

	def __init__(self, aggr_config, namespace="local", config={}):
		super(AMQPInput, self).__init__(aggr_config, namespace, config)
		self.exit = Event()

	def run(self):
		self.log.info("Connecting to (%s): %s" %(self.outputType, self.outputUri))
		aggrConn = self.connectAggregator()

		rabbitmqConsumer = RabbitMQConsumer(**self.config)

		def callback(event):
			if not event.has_key('namespace'):
				event['namespace'] = self.namespace

			aggrConn.send(event)

			if self.exit.is_set():
				aggrConn.close()
				rabbitmqConsumer.stop()

		rabbitmqConsumer.userCallbacks = [ callback ]	
		rabbitmqConsumer.start()

	def shutdown(self):
		self.exit.set()


class ZMQInput(BaseInput):

	log = logging.getLogger("%s.ZMQInput" %(__name__))

	def __init__(self, aggr_config, namespace="local", config={}):
		super(ZMQInput, self).__init__(aggr_config, namespace, config)
		self.exit = Event()

	def startInputServer(self):
		inputServer = ZBase(uri=self.config['uri'], zmqType=self.config['type'])
		self.log.info("Listening on (%s): %s" %(self.config['type'], self.config['uri']))
		inputServer.bind()
		return inputServer

	def __checkRequest(self, reqStr):
		req = json.loads(reqStr)
		if not req.has_key('namespace'):
			req['namespace'] = self.namespace
		if not req.has_key('timestamp'):
			req['timestamp'] = time.time()
		return req

	def run(self):
		self.log.info("Connecting to (%s): %s" %(self.outputType, self.outputUri))
		aggrConn = self.connectAggregator()

		inputServer = self.startInputServer()

		while not self.exit.is_set():
			reqStr = inputServer.sock.recv()
			req = self.__checkRequest(reqStr)
			
			# send event to aggregator
			aggrConn.send(req)
			# respond to client with event sent to aggregator
			inputServer.send(req)

		aggrConn.close()
		inputServer.close()

	def shutdown(self):
		self.exit.set()


