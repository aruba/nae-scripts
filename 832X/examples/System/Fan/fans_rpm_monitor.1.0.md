#### Script File Name: fans\_rpm\_monitor.1.0.py

Script Functionality Guide for Monitoring RPM values of all Fans

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

This Hardware Diagnostic Fan script is intended to monitor the rpm
values of all available fans in the system.

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

Listed below is the high level use case for Monitoring RPM of all Fans
of 8320 switch:

"As an Administrator, I would like to monitor the rpm values of all Fans
in the system and the monitored rpm value of each fan information be
represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic "fans\_rpm\_monitor"
script are Manifest, Parameter Definitions and the Policy Constructor.

The 'Manifest' defines the unique name for this script and
'ParameterDefinitions' has no parameters defined. The 'Policy
Constructor' defines a single Monitor Resource URI to capture the rpm
values of all fans. This monitored data is then plotted in a time-series
chart for analysis purpose.

Note:

- *Fan data needs to be created in OVSDB of P4 docker switch OVA to
  use this script, since Fan details will not be populated in P4
  docker switch. *

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA