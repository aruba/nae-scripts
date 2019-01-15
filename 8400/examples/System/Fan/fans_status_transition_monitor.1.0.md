#### Script File Name: fans\_status\_transition\_monitor.1.0.py

Script Functionality Guide for Monitoring Status of all Fans wherein
status transition from different states are monitored.

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
uninitialized, ok and fault. This script intends to monitor status of
fans when there is transition from one status value to another.

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
Given below is the high level use case for Monitoring Status of all Fans
of 8400X switch:

"As an Administrator, I would like to monitor the status of all Fans
using transition from one status value to another and the monitored
status value of each fan information be represented in a time-series
chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"fans\_status\_transition\_monitor" script are Manifest, Parameter
Definitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script.
- 'ParameterDefinitions' has no parameters defined as the intent of the
script is to monitor all available Fans.
- The 'Policy Constructor' handles the main logic for monitoring the
'Fault' status of all Fans. Conditions are defined such that when there
is a transition from one status value to another value, the agent
executes a action callback for it. Status values like
empty/uninitialized/ok are considered to be normal status of a fan and
other states like fault is considered to be critical status value of a
fan. A data structure named 'fans\_list' is used to list fans which
transited to critical status.

When any fan transit from normal status(empty/uninitialized/ok) to
critical status(fault), then the callback 'fans\_status\_action\_fault'
is invoked. The variable 'fans\_list' is updated with that fan name and
set the agent status to 'Critical' along with displaying CLI output for
'show environment fan' as well as syslog which displays the fan name.
Upon next fan transit to fault status, the agent displays CLI and syslog
with that fan name.

When the fan in faulty status(fault) transit to normal status
values(empty/uninitialized/ok), the fan name in 'fans\_list' is
removed.When all the fans status are set back to any normal status
values and 'fans\_list' is empty, the agent status is set back to
'Normal'.

Note:

- *Fan data needs to be created in OVSDB of P4 docker switch to use
  this script, since Fan details will not be populated in P4
  docker switch.*

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure the right state values are used for transition. For ex, using
state name 'normal' instead of 'ok' is not supported.