#### Script File Name: copp\_statistics\_monitor.1.0.py

Script Functionality Guide for Monitoring Switch Control Plane Policing
(CoPP) statistics

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

This Control Plane Policing (CoPP) statistics monitoring script is
intended to monitor CoPP statistics (number of packets dropped or
passed) for given CoPP class. Switch CLI command 'show copp-policy
statistics' can be executed to know about the supported CoPP classes.
Examples for CoPP class are stp, default, vrrp, sflow, dhcp, bgp-ipv4,
icmp-broadcast-ipv4 etc.

Default CoPP class is in the script ‘total’ which monitors the total
number of packets passed or dropped.

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

Listed below are the high level use cases for CoPP statistics monitoring
on 8400X Switch:

"As an Administrator, I would like to monitor Control Plane Policing
(CoPP) statistics for the configurable CoPP class and statistics for the
given CoPP class to be represented in a time-series chart for analysis
purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main sections of the CoPP statistics script are Manifest,
ParameterDefinitions and the Policy Constructor.

- The ’Manifest’ section defines the unique name for this script with
short description about script purpose. 
- 'ParameterDefinitions' section defines script parameters, in this case CoPP
class name to monitor.
- The 'Policy Constructor' handles the main logic for monitoring CoPP
statistics for the given CoPP class. Statistics (Number of packets
passed and dropped) for the given CoPP class will be presented as a time
series graph for analysis purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
- Ensure to provide valid CoPP class as parameter.
