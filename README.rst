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

* **event-handlers** - User defined custom event handlers.  All custom actions code should be dropped in this directory. 

* **event-handlers.json** - Event subscription and respective handlers configuration.

config.json
===========
The important sections in the configuration are inputs, outputs and aggregator.  Each component of the section contains a **handler** and **config** options.

The handler is the class responsible for managing that particular type of input.

* **inputs**

* **outputs**

* **aggregator**

event-handlers.json
===================
This configuration file contains all events to listen to as well as handlers for each event::

  {
    "event.type": [
      {
        "driver": "<'shell' or 'pyfunc'>",
        "handler": "<path_to_handler>"
      }
    ]
  }

