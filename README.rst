=============
Event Reactor
=============
A system designed to take multiple inputs and publish them to an aggregated output stream which can then be reacted upon with user actions in the form of python code or just shell scripts.


Requirements
============
A running version of mongodb is required as well as zeromq.  Under RedHat the needed packages are called:

* mongodb-org
* zeromq-devel

Before proceeding to the installation you may need to clean out pip temp build directory.  You can do so by issuing the following command::

	rm -rvf /tmp/pip-build-root

The above is the default location on RedHat.  This location may be different based on your distribution.


Installation
============

To install the application, run::

	pip install git+https://github.com/euforia/EventReactor.git


Configuration
=============
The configurations live under **/etc/event-reactor**.

* **config.json** - Global configuration file.

* **event-handlers** - Directory containing custom event handlers. 

* **event-handlers.json** - Event subscription and respective handler configuration.

config.json
-----------
The important sections in the configuration are:

* feeds
* outputs
* aggregator 


event-handlers
--------------
These are custom user handlers.  They are located in the **/etc/event-reactor/event-handlers** directory.  A sample testing.py has been provided.  

To add your own handler,

* Copy your python script into the **/etc/event-reactor/event-handlers**
* Update event-handlers.json with the appropriate information.  *More below*

event-handlers.json
-------------------
This configuration file contains all events to listen to as well as handlers for each event::

  {
    "<event.type>": [
      {
        "driver": "<'shell' or 'pyfunc'>",
        "handler": "<path.to.handler>"
      }
    ]
  }

* event.type - The name of the event to subscribe to.

* driver - This can either be **shell** or **pyfunc**.  

* handler - The shell command or path to python function to be executed.

Drivers
-------

**shell**

If the *shell* **driver** is used, the **handler** should contain a command ro run.  The event will be passed to the command as the last argument in the form of a json string.

**pyfunc**

If the *pyfunc* **driver** is used, the **handler** should contain a path to the python function.  This path should exist under the */etc/event-reactor/event-handlers* directory.

Usage
=====

Startup Scripts
---------------
A system startup script has been included for **pre-RHEL 7** based systems.  The system startup script controls both **router** and **sub** processes.
::
	/etc/init.d/event-reactor [ start | stop | restart | status ]

The celery daemon can be started as follows::

	/etc/init.d/celeryd start

Before starting the celery daemon, make sure the **celery** user exists.  The following command creates the celery user if it doesn't exist::

	( id celery 2>&1 ) > /dev/null || useradd celery;

Executables
-----------

**event-router.py**

Controls the routing of events.  This takes multiple inputs, aggregates them and sends them down a univseral channel.

::
	
	Usage: event-router.py [options]

	Options:
	  -h, --help            show this help message and exit
	  -c CONFIG, --config=CONFIG

**event-sub.py**

This subscribes to the output stream and fires the appropriate handlers based on the event.

::

	Usage: event-sub.py [options]

	Options:
	  -h, --help            show this help message and exit
	  --event-handlers=EVENTHANDLERS
	                        Directory containing event handlers
	  -e EVENTFILTERS, --event-filters=EVENTFILTERS
	                        Event filters config file
	  -u PUBURI, --publisher-uri=PUBURI
	                        URI of publisher to connect to
	  -l LOGLEVEL, --log-level=LOGLEVEL

**fire-event.py**

This is a utility script can be used to fire events into the system.

::

	Usage: fire-event.py [options]

	Options:
	  -h, --help            show this help message and exit
	  -d PAYLOAD, --data=PAYLOAD
	  -e EVENTTYPE, --event-type=EVENTTYPE
	  -n NAMESPACE, --namespace=NAMESPACE
	  -u URI, --uri=URI
	  -z ZMQTYPE, --zmq-type=ZMQTYPE

Design
======
::

	                          :--------------------------:
	      feeders -- PUSH --> | 45454 : PULL             |
	                          |              PUB : 55000 | -- SUB --> subscribers
	custom events -- REQ  --> | 55055 : REP              |
	                          :--------------------------:

