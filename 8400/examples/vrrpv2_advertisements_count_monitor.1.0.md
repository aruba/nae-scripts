#### Script File Name: vrrpv2\_advertisements\_count\_monitor.1.0.py

Script Functionality Guide for Monitoring VRRPv2 Advertisements Count

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

This VRRPv2 Advertisements Count monitor script is intended to monitor
VRRPv2 statistics related to advertisements (Sent/Receive) and zero
priority (Sent/Receive) packet count for the specified VRRP Id and
interface in the system. The interface name can be a physical, vlan or
lag interface.

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

Listed below are the high level use cases for VRRPv2 Advertisements
Count monitoring on 8400x Switches:

As an Administrator, I would like to monitor

1.  VRRPv2 Advertisements sent and receive packet count to make sure it
    is properly sending and receiving advertisements at
    configured intervals.

2.  VRRPv2 Zero Priority sent and receive packet count to make sure that
    current master is participating in VRRP.

 
<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script
specifies the following name:

vrrpv2\_advertisements\_count\_monitor

- 'Parameter Definitions' defines the input parameters to the script. This
script requires the following parameters:

	- vrrp\_id – This parameter specifies VRRPv2 instance unique id.
	Default value is 1

	- port\_name - This parameter specifies the interface that this agent
	will monitor for any VRRP state changes. This can be a physical,
	vlan or lag interface. Default value is 1/1/1

- 'Policy Constructor' defines Monitor Resource URI. This script specifies
monitoring uri's to monitor the following:

	1.  VRRPv2 advertisement Tx Packets

	2.  VRRPv2 advertisement Rx Packets

	3.  VRRPv2 zero priority Tx Packets

	4.  VRRPv2 zero priority Rx Packets

This monitored data is then plotted in a time-series chart for analysis
purpose.
 
<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA