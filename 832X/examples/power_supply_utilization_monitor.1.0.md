#### Script File Name: power_supply_utilization_monitor.1.0.py 
   
Script Functionality Guide for Monitoring System Power Supply Utilization 

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
This System Power Supply Utilization monitoring script is intended to monitor
utilization of all Power Supply Units (PSU) on the switch. Power Supply 
utilization indicates maximum and instantaneous power (in watts) for each PSU. 
 
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
Listed below are the high level use cases for System Power Supply utilization
monitoring on 8320 switch: 

"As an Administrator, I would like to monitor System Power Supply utilization
(maximum and instantaneous power for each power supply unit (PSU) in watts)
and all PSU utilization data be represented in a time-series chart for
analysis purpose."    
   
<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------
The main sections of the System Power Supply Statistics script are Manifest, 
ParameterDefinitions and the Policy Constructor.    

- The ’Manifest’ section defines the unique name for this script with short 
description about script purpose.
- 'ParameterDefinitions' section defines script parameters in this case,
there are no parameters.  
- The 'Policy Constructor' handles the main logic for monitoring System Power
Supply utilization. Maximum and instantaneous power (in watts) for each PSU 
on the switch is presented as a time series chart for analysis. 

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
NA  