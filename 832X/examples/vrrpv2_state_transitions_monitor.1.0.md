#### Script File Name: vrrpv2\_state\_transitions\_monitor.1.0.py

Script Functionality Guide for Monitoring VRRPv2 State Transitions Count

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

This VRRPv2 State Transitions Count monitor script is intended to
monitor VRRPv2 statistics related to state transition count for the
given VRRP Id and interface in the system. The VRRP can be in one of the
following states: Init, Master, Back up. The interface name can be a
physical, van or lag interface.

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

Listed below are the high level use cases for VRRPv2 State Transitions
Count monitoring on 8320 Switches:

As an Administrator, I would like to monitor the count of VRRPv2 state
transited to init, master or backup over a period of time to make sure
VRRP is functioning properly.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script uses the
following name:

vrrp\_state\_transition\_monitor

- 'Parameter Definitions' defines the input parameters to the script. This
script requires the following parameters:

	- vrrp\_id – This parameter specifies VRRPv2 instance unique id.

	- port\_name - This parameter specifies the interface that this agent
	will monitor for any VRRP state changes. This can be a physical,
	vlan or lag interface.

- 'Policy Constructor' defines Monitor Resource URI. This script specifies
monitoring uri's to monitor the following:

	1.  VRRP backup to init count

	2.  VRRP master to init count

	3.  VRRP backup to master count

	4.  VRRP master to backup count

	5.  VRRP init to backup count

	6.  VRRP init to master count

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
