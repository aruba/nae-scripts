#### Script File Name: power\_supply\_monitor.1.0.py

Script Functionality Guide for monitoring System Power Supply Unit (PSU)

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

This Power Supply Monitoring script is intended to monitor status and
statistics of the Switch Power Supply Unit (PSU) provided as input
parameter. Default PSU parameter in script is 'psu-1'.
 

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

Listed below are the high level use cases for System Power Supply
monitoring on 8320 switch:

"As an Administrator, I would like to monitor System Power Supply status
and statistics for the configurable Power Supply Unit (PSU) and
corresponding PSU status, statistics to be represented in a time-series
chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main sections of the Power Supply monitoring script are Manifest,
ParameterDefinitions and the Policy Constructor.

- The ’Manifest’ section defines the unique name for this script with
short description about script purpose. 
- 'ParameterDefinitions' section defines script parameters. In this script, 
PSU name should be provided as parameter (default: ‘psu-1’).
- The 'Policy Constructor' handles the main logic for monitoring System Power 
Supply status and statistics for the given PSU.

Power Supply Unit (PSU) statistics will be presented in the time series
graph to know about number of warnings and failures for the given PSU.
There are conditions in the script to check the status of given PSU and
below actions executed by this script once the status is met

- Agent status is set to Minor/Critical depending upon the criticality of 
the PSU status.

- Switch CLI command ('show environment power-supply') to capture the current 
details of Switch Power Supply.
 
*Note: Power Supply data needs to be created in OVSDB of P4 docker
switch to use this script since Power Supply details will not be
populated in P4 docker switch. *

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure to provide valid PSU name as parameter which is present on the 
Switch 8320