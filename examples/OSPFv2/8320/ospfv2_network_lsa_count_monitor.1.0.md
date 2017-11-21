#### Script File Name: ospfv2\_network\_lsa\_count\_monitor.1.0.py

Script Functionality Guide for Monitoring OSPFv2 Network LSA Count

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

This OSPFv2 Network LSA Count monitor script is intended to monitor
OSPFv2 area statistics related to OSPFv2 network link state
advertisement packet count for specified VRF name , OSPFv2 process id
and OSPFv2 area id in the system.

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

Listed below are the high level use cases for OSPFv2 Network LSA Count
monitoring on 8320 Switches:

As an Administrator, I would like to monitor the count of OSPFv2 LSA
packets to make sure it is properly sending and receiving advertisements
at configured intervals.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script uses the
following name:

ospfv2\_network\_lsa\_count\_monitor

- 'Parameter Definitions' defines the input parameters to the script. This
script requires the following parameters:

	- vrf\_name – This parameter specifies VRF unique name. Default value
	is default

	- ospf\_process\_id - This parameter specifies the OSPFv2 unique
	process id. Default value is 1

	- ospf\_area\_id - This parameter specifies the OSPFv2 unique router
	area id. Default value is 0.0.0.0

- 'Policy Constructor' defines Monitor Resource URI. This script specifies
monitoring uri to monitor the following:

	1.  OSPFv2 Area statistics – Network LSA count

	2.  OSPFv2 Area statistics – Network Summary ASBR LSA Count

	3.  OSPFv2 Area statistics – Network Summary LSA Count

	4.  OSPFv2 Area statistics – Network NSSA LSA Count

	5.  OSPFv2 Area statistics – Network Router LSA Count

This monitored data is then plotted in a time-series chart for analysis
purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA
