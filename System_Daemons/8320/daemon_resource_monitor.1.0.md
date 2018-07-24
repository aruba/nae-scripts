#### Script File Name: daemon\_resource\_monitor.py

Script Functionality Guide for Monitoring System Daemon Resource (CPU/Memory) 
Utilization

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
This System Daemon Resource monitoring script is intended to monitor 5 
configurable system daemons' CPU and Memory utilization (in percentage) 
against configurable CPU/Memory thresholds for configurable time interval.

Default CPU/Memory threshold value in script is 90%. Default time interval is 
30 seconds. Default daemons to monitor in script parameters are 'ops-switchd',
'ovsdb-server', 'hpe-routing', 'arpmgrd' and 'pimd'.

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
Listed below are the high level use cases for System Daemon Resource 
(CPU/Memory) monitoring on 8320 switch:

"As an Administrator, I would like to monitor configurable 5 System Daemons' 
CPU/Memory utilization against configurable CPU/Memory thresholds for 
configurable time interval and daemons’ CPU/Memory utilization to be 
represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------
The main sections of the System Daemon Resource script are 'Manifest',
'ParameterDefinitions' and the 'Policy Constructor'.

The ’Manifest’ section defines the unique name for this script with short 
description about script purpose. 'ParameterDefinitions' section defines 
script parameters in this case, 5 system daemon names, CPU/Memory thresholds
and time interval to consider continuous CPU/Memory utilization against 
CPU/Memory thresholds.

The 'Policy Constructor' handles the main logic for monitoring System Daemons’
resource CPU/Memory utilization against CPU/Memory thresholds for given time 
interval and actions on exceeding threshold values. CPU/Memory utilization of
5 daemons will be presented to the user in a time series chart. Time series 
chart can present at most 8 monitors (daemon CPU/Memory utilization). User 
can select daemon monitors (CPU and Memory) that need to be presented in 
script agent graph. Conditions are defined to check CPU/Memory utilization
against corresponding CPU/Memory thresholds of each given daemon for the given
time interval. When the CPU/Memory threshold is exceeded by any daemon, below
actions are taken by the script

- Agent status is set to Critical.

- Syslog message indicating the daemon that exceeded configured CPU/Memory 
  threshold. 

- CLI - 'show system resource-utilization daemon <daemon>' to capture daemon CPU, 
Memory and File descriptor utilization details. 

Agent alerts about each CPU/Memory threshold exceeding for each monitored 
daemon. Each CPU/Memory threshold condition has clear action defined which 
logs about daemon coming back to normal CPU/Memory utilization from high 
utilization.

Note: Dynamic parameter changes I.e. after agent creation, are not supported
for this script.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on 8320 switch.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure to provide CPU/Memory threshold values in percentage (0 – 100).
- Ensure to provide correct system daemon name as parameter to monitor.

