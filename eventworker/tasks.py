
import logging

from celeryconfig import CONFIG
from celery.decorators import task

from eventreactor.eventhandlers import DriverManager

log = logging.getLogger(__name__)

@task
def testFunction(userString):
	return userString

@task
def executeEventHandler(driver_handler, data):
	driverMgr = DriverManager(event_handlers_dir=CONFIG['event_handlers_dir'])
	response = driverMgr.execDriverHandler(
						driver_handler['driver'], 
						driver_handler['handler'],
						data)
	if response.get('error') != None:
		log.error(str(response))

	return response