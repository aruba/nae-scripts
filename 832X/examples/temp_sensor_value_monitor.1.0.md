#### Script File Name:temp\_sensor\_value\_monitor.1.0.py

Script Functionality Guide for Monitoring Temperature Value of all
Temperature Sensors:

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

This Hardware Diagnostic Temperature Sensor script is intended to
monitor the Temperature of all available Temperature Sensors.

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

Listed below are the high level use cases for Monitoring Temperature
values of all Temperature Sensors of 8320 Switch:

"As an Administrator, I would like to monitor the Temperature Value of
all Temperature Sensor's in the switch and the monitored status
information be represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"temp\_sensor\_value\_monitor.1.0.py" script are Manifest,
ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has no parameters defined.
- The 'Policy Constructor' defines a single Monitor Resource URI to
capture the temperature of all Temperature Sensors. This monitored data
is then plotted in a time-series chart for analysis purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

N/A