
import json
import logging

from kombu import Connection, Exchange, Queue, Consumer
from kombu.mixins import ConsumerMixin

from zmqwrappers import ZBase

class RabbitMQConsumer(ConsumerMixin):

	log = logging.getLogger("%s.RabbitMQConsumer" %(__name__))

	def __init__(self, url, exchange_type, routing_key, queue_name, bindings, callbacks=None, namespace="local"):
		self.namespace = namespace

		exchange 	= Exchange(type=exchange_type)
		
		self.queues  = [ Queue(queue_name, exchange=exchange) ]
		self.connection   = Connection(url)
		
		channel     = self.connection.channel()
		
		bound_queue = self.queues[0].bind(channel)
		bound_queue.declare()
		
		for binding in bindings:
			bound_queue.bind_to(binding, routing_key)

		if callbacks != None:
			if isinstance(callbacks, list):
				self.userCallbacks  = callbacks
			else:
				self.userCallbacks = [ callbacks ]
		else:
			self.userCallbacks = None

		self.log.info("Queue bindings:\n\n\t%s == > %s\n" %(queue_name, bindings))


	def get_consumers(self, Consumer, channel):
		return [Consumer(queues=self.queues, auto_declare=False,
						 			callbacks=[self.processEvent])]
 

	def processEvent(self, body, message):
		#body['event_type'] = "%s.%s" %(self.namespace, body['event_type'])
		for callback in self.userCallbacks:
			callback(body)
		message.ack()

	def start(self):
		self.log.info("Starting openstack event consumer...")
		self.run()

	def stop(self):
		self.log.info("Stopping openstack event consumer...")
		self.should_stop = True
