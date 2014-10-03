
import logging
import json

from multiprocessing import Process, Event

from eventreactor.mqaggr.wrappers.rmqwrappers import RabbitMQConsumer
from eventreactor.mqaggr.wrappers.zmqwrappers import ZBase

from pprint import pprint


class BaseInput(Process):

	def __init__(self, outputUri, outputType="zmq.PUSH", config={}):
		super(BaseInput, self).__init__(group=None, target=None, name=None, args=(), kwargs={})
		self.config = config
		self.outputUri = outputUri
		self.outputType = outputType


class AMQPInput(BaseInput):

	log = logging.getLogger("%s.AMQPInput" %(__name__))

	def __init__(self, outputUri, outputType="zmq.PUSH", config={}):
		super(AMQPInput, self).__init__(outputUri, outputType, config)
		self.exit = Event()

	def run(self):
		zbase = ZBase(uri=self.outputUri, zmqType=self.outputType)
		self.log.info("Connecting to (%s): %s" %(self.outputType, self.outputUri))
		zbase.connect()
		
		rabbitmqConsumer = RabbitMQConsumer(**self.config)

		def callback(event):
			zbase.sock.send(json.dumps(event))
			if self.exit.is_set():
				zbase.close()
				rabbitmqConsumer.stop()

		rabbitmqConsumer.userCallbacks = [ callback ]	
		rabbitmqConsumer.start()


	def shutdown(self):
		self.exit.set()



class ZMQInput(BaseInput):

	log = logging.getLogger("%s.ZMQInput" %(__name__))

	def __init__(self, outputUri, outputType="zmq.PUSH", config={}):
		super(ZMQInput, self).__init__(outputUri, outputType, config)
		self.exit = Event()


	def run(self):
		output = ZBase(uri=self.outputUri, zmqType=self.outputType)
		self.log.info("Connecting to (%s): %s" %(self.outputType, self.outputUri))
		output.connect()

		inputServer = ZBase(uri=self.config['uri'], zmqType=self.config['type'])
		self.log.info("Listening on (%s): %s" %(self.config['type'], self.config['uri']))
		inputServer.bind()

		while not self.exit.is_set():
			reqStr = inputServer.sock.recv()
			
			req = json.loads(reqStr)
			if req.has_key('namespace'):
				req['event_type'] = "%s.%s" %(req['namespace'], req['event_type'])
			else:
				req['event_type'] = "%s.%s" %(self.config['namespace'], req['event_type'])
			
			output.send(req)
			inputServer.send(req)

		inputServer.close()
		output.close()


	def shutdown(self):
		self.exit.set()


