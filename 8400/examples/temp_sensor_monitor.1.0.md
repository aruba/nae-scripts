#### Script File Name: temp\_sensor\_monitor.1.0.py

Script Functionality Guide for Monitoring all attributes of Specific
Temperature Sensor

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

This Hardware Diagnostic Temperature Sensor script is intended to monitor the
status transition and temperature value of a specified temperature sensor. The
supported states being:

- Uninitialized/Normal/Min/Max/Low Critical/Critical/Fault/Emergency.

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

Listed below are the high level use cases for Monitoring Status
Transition and Temperature Value of a specified Temperature Sensor
belonging to 8400x Switch:

"As an Administrator, I would like to monitor the status transition and
temperature value of a specified Temperature Sensor in the switch and
the monitored information be represented in a time-series chart for
analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic "temp\_sensor\_monitor.1.0.py"
script are Manifest, ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has two parameters defined as to indicate the
subsystem type to which the Temperature Sensor belongs to and the Sensor
Name. The parameters are 'sensor\_subsystem\_type' and 'sensor\_name'.
- The 'Policy Constructor' handles the main logic for monitoring the
status transition and temperature value of the specified Temperature Sensor.

The first Monitor Resource URI defined monitors the temperature value of
the Temperature Sensor and no Action is taken corresponding to this. The 
monitored temperature values over time are plotted in a time-series chart for
analysis purpose.

The second Monitor Resource URI defined is to monitor the status transition 
of the specified Temperature Sensor. This monitored data is then plotted in 
a time-series chart for analysis purpose.

When the specific Condition is met a detailed Syslog message indicating
the transition states and output of CLI command ('show system temperature') 
is displayed in Alert Window and the policy Status is changed as per 
transition state severities.

 
<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure the right state is used for transition. For ex, using status
'OK' instead of 'Normal' is incorrect as 'Ok' is not a defined state in 
Temp\_sensor table.

- On 8400x platform, the supported Status transition states are
Uninitialized, Normal, Fault and Critical.

- On P4 docker switches, the supported Status transition states are
Normal, Min, Max, Low\_Critical, Fault, Critical and Emergency.