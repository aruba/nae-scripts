#### Script File Name: port\_admin\_state\_monitor.1.0.py

Script Functionality Guide for monitoring administrative state of a
given port.

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

This port admin state monitor script is intended to monitor administrative 
state change happening on the supplied port. The port admin state determines 
the hardware configuration based on the business logic. This state can be 
either "up" or "down".

<a id='Prerequisites'></a>
#### Prerequisites:

------------------------------------------------------------------------------

- Working knowledge of Python language to understand the script and have 
access to any editor for writing/modifying python scripts.

- Set up the scripts execution environment using the switch management access 
of the 8320 switches.

- Knowledge of how to upload the script using either the switch Web User 
Interface/REST API's.

- Knowledge of how to create an agent using either switch Web User 
Interface/REST API's.

<a id='Use_Case'/></a>
#### Use Case(s):
------------------------------------------------------------------------------

Listed below are the high level use case for monitoring administrative state 
change happening on the supplied port of the Switch:

"As an administrator I would like to view and monitor administrative state 
change happening on the supplied port in my switch. I should be able to view 
the state change information on the graph and get alerts if a port's 
administrative state changes from "up" to "down".

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of port admin state monitor script are Manifest, Parameter
Definition and the Policy Constructor.

- The 'Manifest' defines the unique name for this script.

- 'ParameterDefinitions' section defines the following script parameters

	- 'port\_id' -&gt; specifies the port id of the port to be monitored.
	The default id is 1/1/1

- The 'Policy Constructor' handles the main logic for monitoring the 
administrative state change happening on the supplied port in the system.

Condition is defined to monitor 'admin' state of the supplied port. 'admin' 
state specifies whether the given port is administratively "up" or "down". 
If the administrative state of the given port transitions from "up" to "down"
then the following actions are taken :

- Agent status is set to Critical.

- Syslog messages is written indicating that the administrative state
of the supplied port.

- CLI commands executed to capture lldp configuration and extended information
of the given port.

If the administrative state of given port comes back to the state "up" then 
the agent status is set back to Normal.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------

This script has been tested on platforms 8320.


<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure that as part of successful configuration, administrator is able to 
instantiate agents without any errors and is able to view monitored values 
plotted as data points on time series charts for analysis purpose in the 
WEB-UI. 
- Ensure that the given interface ID is valid.
