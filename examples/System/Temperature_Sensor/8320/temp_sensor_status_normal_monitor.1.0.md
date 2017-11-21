#### Script File Name: temp\_sensor\_status\_normal\_monitor.1.0.py

Script Functionality Guide for Monitoring Normal Status of all
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

This Hardware Diagnostic Temperature Sensor script is intended to monitor the 
status transition of all available temp sensors from various supported states
(Low\_Critical/Critical/Fault/Emergency) to 'Normal' state 
(to any of Min/Max/Normal/Uninitialized).

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

Listed below are the high level use cases for Monitoring 'Normal' Status
of all Temperature Sensors of 8320 Switch:

"As an Administrator, I would like to monitor the transition of
Temperature Sensor Status of all Sensors from 'Critical' status
(Low\_Critical/Critical/Fault/Emergency states) to 'Normal' status
(Uninitialized/Max/Min/Normal states) and the monitored status
information be represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"temp\_Sensor\_monitor\_status\_normal\_monitor.1.0.py" script are
Manifest, ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has no parameters defined as the intent of the
script is to monitor available Temp Sensors.
- The 'Policy Constructor' handles the main logic for monitoring the
'Normal' status of all Temp Sensors.

Conditions are defined to verify the transition state.

When any temp sensor transitions to any of the critical states, then the
call back 'sensr\_action\_status\_critical' is invoked. Within this
callback a data structure referred to as 'sensors\_list' is maintained
to store the list of all Sensors names whose status is in any of the
'Low\_Critical/Critical/Fault/Emergency' states and policy is set to
'Critical' state along with display of CLI command 'show system
temperature') result in Alert Details. When the same temp sensor
transitions back to any of the Normal states
(Min/Max/Normal/Uninitialized), then that sensor name is removed from
the 'sensors\_list' data structure and policy is set back to 'Normal'
status.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure the right state is used for transition. For ex, using status
'OK' instead of 'Normal' is incorrect as 'Ok' is not a defined state in 
'Temp\_sensor' OVSDB table.

- On 8320 switches, the supported status transition states are
Uninitialized, Normal, Fault and Critical.

- On P4 docker switches, the supported status transition states are
Normal, Min, Max, Low\_Critical, Fault, Critical and Emergency.