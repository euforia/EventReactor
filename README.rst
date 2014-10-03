=============
Event Reactor
=============
A system designed to take multiple inputs and publish them to an aggregated output stream which can then be reacted upon with user actions in the form of python code or just shell scripts.


Installation
============

* pip install git+https://github.com/euforia/EventReactor.git


Configuration
=============
The configurations live under **/etc/event-reactor**.

* **config.json** - Global configuration file.

* **event-handlers** - This directory contains user defined custom event handlers. 

* **event-handlers.json** - Event subscription and respective handlers configuration.

config.json
===========
The important sections in the configuration are inputs, outputs and aggregator.  Each component of the section contains a **handler** and **config** options.

The handler is the class responsible for managing that particular type of input.

* **inputs**

* **outputs**

* **aggregator**

event-handlers
==============
These are custom user handlers.  They are located in the **/etc/event-reactor/event-handlers** directory.  A sample testing.py has been provided.  

To add your own handler,

* Copy your python script into the **/etc/event-reactor/event-handlers**
* Update event-handlers.json with the appropriate information.  *More below*

event-handlers.json
===================
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

* driver - This can either be 'shell' or 'pyfunc'.  
	* shell - Allows to run arbitrary shell scripts on an event
	* pyfunc - Allows to run a python function

* handler
	* shell
	* pyfunc


