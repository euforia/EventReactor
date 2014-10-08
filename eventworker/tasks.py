
from celeryconfig import CONFIG
from celery.decorators import task

from eventreactor.eventhandlers import DriverManager

@task
def testFunction(userString):
	return userString

@task
def executeEventHandler(driver_handler, data):
	driverMgr = DriverManager(event_handlers_dir=CONFIG['event_handlers_dir'])
	return driverMgr.execDriverHandler(
						driver_handler['driver'], 
						driver_handler['handler'],
						data)
	