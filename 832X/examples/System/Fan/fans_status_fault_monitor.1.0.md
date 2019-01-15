#### Script File Name: fans\_status\_fault\_monitor.1.0.py

Script Functionality Guide for Monitoring Status of all Fans

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

This Hardware Diagnostic Fan script is intended to monitor the status of
all available fans with various supported states like empty,
uninitialized, fault and ok.

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

- Knowledge of how to fetch fan details of the switch. Fan details of the 
Switch are available in Switch Web-UI Overview page or can be retrieved using 
Switch REST Interface for Fan. 

<a id='Use_Case'/></a>
#### Use Case(s):

------------------------------------------------------------------------------

Listed below is the high level use case for Monitoring status of all
Fans of 8320 switch:

"As an Administrator, I would like to monitor the status of all Fans and
the monitored status value of each fan and information be represented in
a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------
The main components of the Hardware Diagnostic
"fans\_status\_fault\_monitor" script are Manifest, Parameter
Definitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has no parameters defined as the intent of the
script is to monitor all available Fans.
- The 'Policy Constructor' handles the main logic for monitoring the 'Fault'
state value of all Fans.

Condition is defined to monitor 'Fault' status of each fan. A data
structure named 'fans\_list' is used to list fans which transited to
fault state and 'faulty\_fans\_count' is used to count the number of
fans which are at fault state.

When any fan transit to fault state, then the callback
'fans\_status\_action\_fault' is invoked. The variable 'fans\_list' is
updated with that fan name and 'faulty\_fans\_count' is incremented and
set the agent status to 'Critical' along with displaying CLI output for
'show environment fan' as well as syslog which displays the fan name and
number of fans at faulty state. Upon next fan transit to faulty, the
agent displays CLI and number of fans which are faulty.

When the same fan at fault state transit back to status value other than
'fault', then clear\_action is executed in which the fan name in
'fans\_list' is removed and 'faulty\_fans\_count' is decremented. When
all the fans status are set back to any status value other than 'fault'
and 'fans\_list' is empty, then clear\_action is executed where the
agent status is set back to 'Normal'.

Note:

- *Fan data needs to be created in OVSDB of* P4 docker switch *to use
  this script, since Fan details will not be populated in* P4 docker
  switch*.*

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure the right state values are used for transition. For ex, using
state name 'Ok' instead of 'Normal' is not supported.