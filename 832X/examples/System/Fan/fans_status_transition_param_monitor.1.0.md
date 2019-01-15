#### Script File Name: fans\_status\_transition\_param\_monitor.1.0.py

Script Functionality Guide for Monitoring Status of all Fans wherin
transition "from" and "to" values are supplied as parameters.

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
fans when there is transition from one status value to another is
supplied by an user as parameters.

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

Given below is the high level use case for Monitoring Status of all Fans
of 8320 switch:

"As an Administrator, I would like to monitor the status of all Fans
using transition from one status value to another, wherein transition
"from" and "to" values are supplied as parameters. The monitored status
value of each fan information be represented in a time-series chart for
analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"fans\_status\_transition\_param\_monitor" script are Manifest,
Parameter Definitions and the Policy Constructor.

The 'Manifest' defines the unique name for this script. The 'Parameter
Definitions' has parameters like "transition\_from" and "transition\_to"
which is supplied in the transition condition for "from" and "to"
respectively. The parameters values can be empty/uninitialized/ok/fault.
The default value for "transition\_from" and "transition\_to" are "ok"
and "fault" respectively.

The 'Policy Constructor' handles the main logic for monitoring the
transition from one status value to another status value as supplied by
the user in as parameters. User can monitor the transition of each fan
from one state to another of there interest as supplied by the user in
the parameters.

When the transition condition is met, action "fan\_status\_action" is
invoked. This action displays CLI output for 'show environment fan', as
well as syslog which displays the fan name which took transition from
one status value to another as expected by the user.

Note:

- *Fan data needs to be created in OVSDB of P4 docker switch to use
  this script, since Fan details will not be populated in P4
  docker switch.*

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
- Ensure the right state values are used for transition. For ex, using
state name 'normal' instead of 'ok' is not supported.

- Make sure that the default values provided while creating agent are
present. If not update the fields before creating an agent. If default
values provided are absent, then the agent error is seen.