#### Script File Name: interface\_queues\_monitor.1.0.py

Script Functionality Guide for monitoring egress queues of an interface.

==============================================================================

### Contents
------------------------------------------------------------------------------
- [Overview](#Overview)
- [Prerequisites](#Prerequisites)
- [Use Case(s)](#Use_Case)
- [Functional Description](#Functional_Description)
- [Platform(s) Supported](#Platforms_Supported)
- [Error-Handling](#Error-Handling)

<a id='Overview'></a>
#### Overview:

------------------------------------------------------------------------------

This Interface queue stats monitor script is intended to monitor egress
queues of an interface and reports the counters of tx bytes, tx packets
& tx errors.

<a id='Prerequisites'></a>
#### Prerequisites:
------------------------------------------------------------------------------

- Working knowledge of Python language to understand the script and have 
access to any editor for writing/modifying python scripts.

- Set up the scripts execution environment using the switch management access 
of the 8400x switches.

- Knowledge of how to upload the script using either the switch Web User 
Interface/REST API's.

- Knowledge of how to create an agent using either switch Web User 
Interface/REST API's.

<a id='Use_Case'/></a>
#### Use Case(s):

------------------------------------------------------------------------------

Listed below are the high level use case for Monitoring egress queues of
an interface on 8400x Switch:

"As an administrator I would like to view and monitor egress queues
statistics of an interface and report the counters of queue\_tx\_bytes,
queue\_tx\_packets & queue\_tx\_errors which will be shown on the graph.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of Interface queue Monitor script are Manifest,
Parameter Definition and the Policy Constructor.

- The 'Manifest' defines the unique name for this script.
     
- 'ParameterDefinitions' section defines the following script parameters

	- interface\_id  -&gt; specifies the Interface id whose queues will be
	monitored. The default value is set to "1/1/1".
     
- The 'Policy Constructor' handles the main logic for monitoring the egress
queues of an interface.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

-   Ensure that the given interface ID is valid.


