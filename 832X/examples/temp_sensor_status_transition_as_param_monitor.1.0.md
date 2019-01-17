#### Script File Name: temp\_sensor\_status\_normal\_monitor.1.0.py

Script Functionality Guide for Monitoring Specific Status Transition of
all Temperature Sensors

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
status transition of all available temp sensors for a specific 'Source' state
to 'Destination' state as chosen by the Administrator.

The supported states being
Min/Max/Normal/Uninitialized/Low\_Critical/Critical/Fault/Emergency.

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

Listed below is the high level use cases for Monitoring Status
Transitions of all Temperature Sensors of  8320 Switch:

"As an Administrator, I would like to monitor Status Transition of all
Temperature Sensor's from a specific chosen 'Source State' to
'Destination State' and the monitored status information be represented
in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the Hardware Diagnostic
"temp\_sensor\_status\_transition\_as\_param\_monitor.1.0.py" script are
Manifest, ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has two parameters defined to indicate the source
and destination transition states to monitor. The parameters are
'transition\_from' and 'transition\_to'.
- The 'Policy Constructor' handles the main logic for monitoring the
specific status transition of all Temp Sensors. Conditions are defined
to verify the transition from chosen 'From\_state' to 'To\_state' state.

When the specific Condition is met a detailed Syslog message indicating
the transition states and output of CLI command ('show system
temperature') is displayed in Alert Window and the policy Status is not
changed as per transition state severities and remains in 'Normal' state
only.

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

- On 8320 platform, the supported Status transition states are
Uninitialized, Normal, Fault and Critical.

- On P4 docker switches, the supported status transition states are
Normal, Min, Max, Low\_Critical, Fault, Critical and Emergency.