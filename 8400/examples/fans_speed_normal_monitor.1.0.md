#### Script File Name: fans\_speed\_normal\_monitor.1.0.py

Script Functionality Guide for Monitoring Speed of all Fans

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

This Hardware Diagnostic Fan script is intended to monitor the speed of all 
available fans with various supported states like slow, medium, normal, fast
and max.

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

Listed below is the high level use case for Monitoring Speed state of
all Fans of 8400X switch:

"As an Administrator, I would like to monitor the speed of all Fans and
the monitored speed value of each fan information be represented in a 
time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"fans\_speed\_normal\_monitor" script are Manifest, ParameterDefinitions and 
the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has no parameters defined as the intent of the
script is to monitor all available Fans.
- The 'Policy Constructor' handles the main logic for monitoring the
'Normal' speed value of all Fans. Conditions are defined such that each
speed state is monitored. States like slow/medium/normal are considered
to be normal speed of a fan and other states like fast/max are
considered to be critical speed values of a fan.

A data structure named 'fans\_list' is used to list fans which transited
to critical speed state and 'speedy\_fans\_count' is used to count the
number of fans which are at high speed.

When any fan transit to any critical speed value, then the callback
'fans\_speed\_action\_high' is invoked. The variable 'fans\_list' is
updated with that fan name and 'speedy\_fans\_count' is incremented and
set the agent status to 'Critical' along with displaying CLI output for
'show environment fan' as well as syslog which displays the fan name and
number of fans at high speed. Upon next fan transit to high speed value,
the agent displays CLI and number of fans at high speed.

When the fan at high speed transit to normal speed (slow/medium/normal),
the fan name in 'fans\_list' is removed and 'speedy\_fans\_count' is
decremented. When all the fans speed are set back to any normal speed
value and 'fans\_list' is empty, the agent status is set back to
'Normal'.

Note:

- *Fan data needs to be created in OVSDB of P4 docker switch to use
  this script, since Fan details will not be populated in P4 docker
  switch.*

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure the right state values are used for transition. For ex, using
state name 'Ok' instead of 'Normal' is not supported.