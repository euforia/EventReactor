
import logging

from pprint import pprint

log = logging.getLogger(__name__)


def dumpEvent(event):
	log.info("Data ==> %s" %(str(event)))
	return event

def dumpEventPayload(event):
	if event.has_key('payload'):
		log.info("Data ==> %s" %(str(event['payload'])))
	else:
		log.info("Data ==> {}")
