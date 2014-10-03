
import logging
import zmq
import json

class ZBase(object):

	log = logging.getLogger("%s.ZBase" %(__name__))

	def __init__(self, uri, zmqType, **kwargs):
		self.uri = uri
		self.zmqType = zmqType
		self.__extras = kwargs

		ctxt = zmq.Context()		
		
		self.sock = ctxt.socket(eval(self.zmqType))

		if self.zmqType == "zmq.SUB":
			if not self.__extras.has_key('topics'):
				self.__extras['topics'] = ['']


	def bind(self):
		self.log.info("Listening on: '%s'" %(self.uri))
		self.sock.bind(self.uri)


	def connect(self):
		self.log.info("Connecting to: '%s'" %(self.uri))
		self.sock.connect(self.uri)
		if self.zmqType == "zmq.SUB":
			for topic in self.__extras['topics']:
				self.sock.setsockopt(zmq.SUBSCRIBE, topic)


	def send(self, data, topic=''):
		
		payload = None
		if isinstance(data, str) or isinstance(data, unicode):
			payload = data
		else:
			if topic == '' or topic == None:
				payload = json.dumps(data)
			else:
				payload = "%s %s" %(topic, json.dumps(data))

		self.sock.send(payload)


	def close(self):
		self.sock.close()
