#### Script File Name: interface\_state\_stats\_monitor.1.0.py

Script Functionality Guide for monitoring link state and packets
statistics of the given interface.

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

This interface state stats monitor script is intended to monitor link state of
the given interface and packets being transmitted, received and dropped on
that interface.


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

Listed below are the high level use case for monitoring flapping links of
the Switch:

"As an administrator I would like to monitor the links state and Tx/Rx packet 
stats of given interface in my switch. I should be able to view the state of 
the link which will be either "up" or "down" and also the Tx/Rx packets count 
on the graph. I should get an alert if an Interface link state changes from 
Up to Down or Down to Up".

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of interface state stats monitor script are Manifest, 
Parameter Definition and the Policy Constructor.

- The 'Manifest' defines the unique name for this script. 

- 'ParameterDefinitions' section defines the following script parameters

	- 'interface\_id' -&gt; This is the interface name/ID that needs to be
	monitored. The default value is 1/1/1.

- The 'Policy Constructor' handles the main logic for monitoring the link 
state and Tx/Rx stats of the given interface.

Condition is defined to monitor 'link\_state' of the supplied interfaces. 
'link\_state' specifies the Link's carrier status of an interface. If the link
state of the given interface transitions from "up" to "down" then the 
following actions are taken :

- Agent status is set to Critical.

- Syslog messages is written indicating that the link state of an interface
is gone down.

- CLI commands executed to capture lldp configuration and extended information
of the given interface.

If the link state of given interfaces comes back to the state "up" then the 
agent status is set back to Normal.

The agent chart displays the link state and and Tx/Rx statistics. This 
information can be used to monitor the health of the given interface.
 
<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.


<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure that as part of successful configuration, administrator is able to 
instantiate agents without any errors and is able to view monitored values 
plotted as data points on time series charts for analysis purpose in the 
WEB-UI. 
- Ensure that the given interface ID is valid.