
import sys
import json
import subprocess

from pprint import pprint

class HandlerDriver(object):

	def __init__(self, driver_type):
		self.driverType = driver_type

	def applyDefaultAttrs(self, attrs={}):
		return dict([(k,v) for k,v in attrs.items()] + [ 
							("driver_type", self.driverType) ])

	def process(self, event):
		pass


class PythonFuncDriver(HandlerDriver):

	def __init__(self):
		super(PythonFuncDriver, self).__init__("pyfunc")

	def execHandler(self, handler, event):
		try:
			#mod_name = "eventreactor.eventhandlers.pyfunc.%s" %(".".join(handler.split(".")[:-1]))
			mod_name = ".".join(handler.split(".")[:-1])
			os_mod = __import__(mod_name, fromlist=[mod_name])
			return self.applyDefaultAttrs({
				"code": 0,
				"data": eval("os_mod.%s(event)" %(handler.split(".")[-1])),
				"handler": handler
			})
		except Exception,e:
			return self.applyDefaultAttrs({ 
					"error": True, "data": str(e), "handler": handler })


class ShellDriver(HandlerDriver):

	def __init__(self):
		super(ShellDriver, self).__init__("shell")

	def execHandler(self, handler, event):

		cmdArr = handler.split() + [ json.dumps(event) ]
		sproc = subprocess.Popen(cmdArr, stdout=subprocess.PIPE, 
											stderr=subprocess.PIPE)
		stdout, stderr = sproc.communicate()
		if sproc.returncode != 0:
			return self.applyDefaultAttrs({ "error": sproc.returncode, "data": stderr })
		else:
			return self.applyDefaultAttrs({	"code": sproc.returncode, "data": stdout })


class DriverManager(object):

	driverTypes = ("pyfunc", "shell")

	def __init__(self, event_handlers_dir=''):
		#self.driverTypes = supported_types
		self.drivers = {}
		for dtype in self.driverTypes:
			if dtype == "shell":
				self.drivers[dtype] = ShellDriver()
			elif dtype == "pyfunc":
				self.drivers[dtype] = PythonFuncDriver()

		if event_handlers_dir != "" and event_handlers_dir not in sys.path:
			sys.path.append(event_handlers_dir)


	def execDriverHandler(self, driver_type, handler, event):
		return self.drivers[driver_type].execHandler(handler, event)


class EventFilterManager(object):
	
	def __init__(self, listen_filters):
		self.listenEvents = listen_filters
		# set default exclusive
		for k, handlers in self.listenEvents.items():
			for h in handlers:
				if not h.has_key('exclusive'):
					h['exclusive'] = False


	def eventHandlers(self, event):
		## get from some sort of db.
		if self.listenEvents.has_key(event['event_type']):
			return self.listenEvents[event['event_type']]
		else:
			return []
