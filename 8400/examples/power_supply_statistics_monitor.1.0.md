#### Script File Name: power\_supply\_statistics\_monitor.1.0.py

Script Functionality Guide for Monitoring System Power Supply statistics

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

This System Power Statistics monitoring script is intended to monitor
statistics of all Power Supply Units (PSU) on the switch. Power Supply
statistics indicate number warnings and failures for PSU.

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
Statistics monitoring on 8400X switch:

"As an Administrator, I would like to monitor System Power Supply
statistics (warnings and failures for each PSU) and all PSU statistics
data be represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main sections of the System Power Supply Statistics script are
Manifest, ParameterDefinitions and the Policy Constructor.

- The ’Manifest’ section defines the unique name for this script with
short description about script purpose. 
- 'ParameterDefinitions' section defines script parameters in this case, 
there are no parameters.
- The 'Policy Constructor' handles the main logic for monitoring System
Power Supply statistics. Number of warnings and failures for each PSU on
the switch is presented as a time series chart for analysis.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA