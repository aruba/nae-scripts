#### Script File Name: fan\_monitor.1.0.py

Script Functionality Guide for Monitoring all attributes of Specific Fan

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

This Hardware Diagnostic Fan script is intended to monitor the status,
speed and rpm value of a specified fan. The supported states for speed
are slow, medium, normal, fast and max. Supported states for status are
empty, uninitialized, ok and fault.

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

- Knowledge of how to fetch fan details of the switch. Fan details of the 
Switch are available in Switch Web-UI Overview page or can be retrieved using 
Switch REST Interface for Fan. 

<a id='Use_Case'/></a>
#### Use Case(s):

------------------------------------------------------------------------------

Listed below is the high level use case for Monitoring speed, status and
rpm value of a specified Fan belonging to 8400X switch:

"As an Administrator, I would like to monitor speed, status and rpm
value of a specified Fan and the monitored information be represented in
a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic "fan\_monitor" script are
Manifest, ParameterDefinitions and the Policy Constructor.

The 'Manifest' defines the unique name for this script and
'ParameterDefinitions' has one parameter named 'fan\_name' to indicate
the fan name of which the speed, status and rpm values to be monitored.
The default value for the parameter 'fan\_name' in case of 8400x switch
is 1/1/1 , which belongs to fan\_tray 1/1 .

The 'Policy Constructor' handles the main logic for monitoring the
speed, status and rpm value of the specified Fan. The first Monitor
Resource URI defined is to monitor the status transition of the
specified Fan. This monitored data is plotted in a time-series chart for
analysis purpose. The agent status will be set to 'critical' when the
fan status value transited to 'fault'.

The second Monitor Resource URI defined is to monitor the speed
transition of the specified Fan. This monitored data is plotted in a
time-series chart for analysis purpose. The agent status will be set to
'major' when fan speed value transited to 'fast' and 'critical' when the
fan speed value transited to 'max'.

The third Monitor Resource URI defined monitors the rpm value of the Fan
and no Action is taken corresponding to this. The monitored rpm value
over time is plotted in a time-series chart for analysis purpose.

When the specific Condition is met a detailed Syslog message indicating
the transition states and output of CLI command ('show environment fan')
is displayed in Alert Window and the agent status is changed as per
transition state severities.

Note :

- *The priority order in increasing order to set agent status is 
Critical &gt; Major.*

 	*e.g. When the fan status is already 'fault' and speed value transits
 	to 'fast/max', the agent status will not change to Critical again,
 	since the agent status is already in Critical state.*

  

- *Fan data needs to be created in OVSDB of P4 docker switch to use
  this script, since Fan details will not be populated in P4
  docker switch. *

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure to provide valid fan name as parameter which is present on
  the 8400X/P4 docker switch.

- Make sure that default value provided while creating agent
  is present. If not update the field before creating an agent. If
  default fan name provided is absent, then the agent error is seen.