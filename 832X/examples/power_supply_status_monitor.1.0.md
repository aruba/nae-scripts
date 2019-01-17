#### Script File Name: power\_supply\_status\_monitor.1.0.py

Script Functionality Guide for Monitoring System Power Supply Status

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

This System Power Supply Status monitoring script is intended to monitor
status of all Power Supply Units (PSU). PSU states are ‘ok’,
‘fault\_output’ (Output Fault), ‘fault\_input’ (Input Fault), ‘warning’,
‘unknown’, ‘unsupported’ and ‘fault\_absent’ (Absent).

*Note: Power Supply details of the Switch are available in Switch Web-UI
Overview page or can be retrieved using Switch REST Interface for Power
Supply.*

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

Listed below are the high level use cases for System Power Supply Status
monitoring on 8320 switch:

"As an Administrator, I would like to monitor System Power Supply status
and status of all Power Supply Units (PSU) to be represented in a
time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------
The main sections of the System Power Supply Status script are Manifest,
ParameterDefinitions and the Policy Constructor. 

- The ’Manifest’ section defines the unique name for this script with short
description about script purpose. 
- 'ParameterDefinitions' section defines script parameters. In this script, 
there are no parameters.
- The 'Policy Constructor' handles the main logic for monitoring System
Power Supply status i.e. status of all Power Supply Units (PSU) in the
switch. 

Conditions are there in the script to check the various states 
(OK, Unknown, Input Fault, Output Fault, Warning etc) of Power Supply Units. 
Once a status condition is met, below actions are taken

- If Power Supply Unit (PSU) status is Warning/Unsupported/Unknown,
 agent status is set to Warning. But if Power Supply Unit (PSU)
 status is 'Input Fault'/'Output Fault', agent status is set
 to Critical. Agent status reflects the overall status of all Power
 Supply Units.

- Syslog indicating the Power Supply Unit (PSU) name and its
  current status.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA