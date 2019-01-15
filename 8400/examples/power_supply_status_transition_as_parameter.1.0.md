#### Script File Name: power\_supply\_status\_transition\_as\_parameter.1.0.py

Script Functionality Guide for Monitoring System Power Supply
Parametrized Status Transition

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

This System Power Supply parametrized status transition monitoring
script is intended to monitor Power Supply Unit (PSU) status transition
provided as script parameter (‘transition\_from\_state’ to
‘transtion\_to\_state’). PSU states are ‘ok’, ‘fault\_output’,
‘fault\_input’, ‘warning’, ‘unknown’, ‘unsupported’ and ‘fault\_absent’.

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
Listed below are the high level use cases for System Power Supply
parametrized status transition monitoring on 8400X switch:

"As an Administrator, I would like to monitor System Power Supply status
transition for the PSU status transition provided as input parameter
('from state' and 'to state') and all Power Supply Units’ (PSU) status
to be represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------
The main sections of the System Power Supply parametrized status
transition script are Manifest, ParameterDefinitions and the Policy
Constructor.

The ’Manifest’ section defines the unique name for this script with
short description about script purpose. 'ParameterDefinitions' section
defines script parameters. In this script, parameters are PSU transition
‘from state’ and PSU transition ‘to state’.

The 'Policy Constructor' handles the main logic for monitoring System
Power Supply status transition for the provided status transition as
parameter. Status of all Power Supply Units will be presented to the
user as a time series chart. Single transition condition is there to
check if the status transition provided as input occurred for any Power
Supply Unit present on the switch.

 

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
-   Ensure to provide valid PSU ‘status from’ and ‘status to’ parameters.