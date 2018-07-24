#### Script File Name: interface\_link\_flap\_monitor.1.0.py

Script Functionality Guide for monitoring link flaps in the system.

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

This interface link flap monitor script is intended to monitor link flap 
happening on any interface in the system. The common cause of link flap is a 
Layer 1 issues such as a bad cable, duplex mismatch etc...

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

Listed below are the high level use case for monitoring flapping links of the 
Switch:

"As an administrator I would like to view and monitor flapping links in my 
switch. I should be able to view the rate of flap information on the graph and
get alerts if the flapping rate exceed the configured threshold."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of interface link flap monitor script are Manifest, 
Parameter Definition and the Policy Constructor.

- The 'Manifest' defines the unique name for this script. 

- 'ParameterDefinitions' section defines the following script parameters

	- 'link\_flap\_threshold' -&gt; specifies the link state resets per 
	second, that is an anomalous level for the link. The default value 
	is 1.

	- 'rate\_interval' -&gt; specifies the time interval, in seconds, used
	for calculating the link state reset rate for the interface. 
	The default value is 10.

The 'Policy Constructor' handles the main logic for monitoring the flapping 
links.

Condition is defined to monitor 'link\_resets' count of all interfaces. 
'link\_resets' specifies the number of times Switch has observed the link 
state change from "up" to "down".

If the rate of 'link\_resets' count over the time interval 'rate\_interval' 
(specified in the parameter) increases beyond the specified threshold 
'link\_flap\_threshold' then an the following actions are taken :

- Agent status is set to Critical.

- Syslog messages is written indicating the link flap happing on the
particular interface.

If the rate of 'link\_resets' count over the time interval 'rate\_interval' 
falls below the specified threshold 'link\_flap\_threshold' then the agent 
status is set back to Normal.


<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

N/A
