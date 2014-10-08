
import os

from eventreactor.conf import loadConfig

CONFIG_FILE = os.environ.get('EVENT_REACTOR_CONFIG')
if CONFIG_FILE == None:
	CONFIG_FILE = "/etc/event-reactor/config.json"
	if not os.path.exists(CONFIG_FILE):
		raise RuntimeError("Could not find config file: %s" %(CONFIG_FILE))

CONFIG = loadConfig(CONFIG_FILE)

BROKER_URL = "%(protocol)s://%(host)s:%(port)d/%(database)s" %(CONFIG['celery'])

CELERY_RESULT_BACKEND = "%(protocol)s://%(host)s:%(port)d/" %(CONFIG['celery'])
CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': CONFIG['celery']['database'],
    'taskmeta_collection': CONFIG['celery']['task_collection'],
}
CELERY_TASK_RESULT_EXPIRES = 172800 # 24 hours

CELERY_IMPORTS = CONFIG['celery']['task_imports']

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
	