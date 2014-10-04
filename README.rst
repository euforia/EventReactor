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

* **event-handlers** - Directory containing custom event handlers. 

* **event-handlers.json** - Event subscription and respective handler configuration.

config.json
-----------
The important sections in the configuration are inputs, outputs and aggregator.  Each component of the section contains a **handler** and **config** options.

The handler is the class responsible for managing that particular type of input.

* **inputs**

* **outputs**

* **aggregator**

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

**/etc/init.d/event-reactor**

This is the system startup script that controls both *router* and *sub* processes.

Executeables
------------

**event-router.py**

Controls the routing of events.  This takes multiple inputs, aggregates them and sends them down a univseral channel.

**event-sub.py**

This subscribes to the output stream and fires the appropriate handlers based on the event.

**fire-event.py**

This is a utility script can be used to fire events into the system.

