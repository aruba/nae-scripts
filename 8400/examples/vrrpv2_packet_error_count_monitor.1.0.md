#### Script File Name: vrrpv2\_packet\_error\_count\_monitor.1.0.py

Script Functionality Guide for Monitoring VRRPv2 Packet Error Count
Monitor

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

This VRRPv2 Packet Error Count monitor script is intended to monitor
VRRPv2 statistics related to invalid, error or mismatch packet count
for the specified VRRP Id and interface in the system. The interface
name can be a physical, vlan or lag interface.

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

Listed below are the high level use cases for VRRPv2 Packet Error
Count monitoring on 8400x Switches:

As an Administrator, I would like to monitor

	1.  Number of times VRRPv2 Advertisement packets are sent at an
	incorrect interval.

	2.  Number of times VRRPv2 Advertisement packets are received in
	init state.

	3.  Number of VRRPv2 packets with invalid length.

	4.  Number of VRRPv2 packets with TTL errors.

	5.  Number of received VRRPv2 packets of invalid type.

	6.  Number of VRRPv2 packets with IP address owner conflicts.

	7.  Number of VRRPv2 packets with incorrect virtual IP address lists.

	8.  Number of VRRPv2 packets with a non-matched authentication mode.

	9.  Number of Near Failovers statistic. A “near failover” is one that is
	within one missed VRRP advertisement packet of beginning the
	Master determination process.

	10. Number of other errors statistics.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script uses
the following name:

vrrpv2\_packet\_error\_count\_monitor

- 'Parameter Definitions' defines the input parameters to the script.
This script requires the following parameters:

	1.  vrrp\_id – This parameter specifies VRRPv2 instance unique id.
	    Default value is 1

	2.  port\_name - This parameter specifies the interface that this agent
	    will monitor for any VRRP state changes. This can be a physical,
	    vlan or lag interface. Default value is 1/1/1

	3.  advertise\_interval\_errors – This parameter specifies the number of
	    times VRRPv2 Advertisement packets are sent at an
	    incorrect interval. Default value is 1, monitoring can be turned
	    off by specifying value 0

	4.  advertise\_recv\_in\_init\_state - This parameter specifies the
	    number of times VRRPv2 Advertisement packets are received in
	    init state. Default value is 0, monitoring can be turned on by
	    specifying value 1

	5.  advertise\_recv\_with\_invalid\_len - This parameter specifies the
	    number of VRRPv2packets with invalid length. Default value is 0,
	    monitoring can be turned on by specifying value 1

	6.  advertise\_recv\_with\_invalid\_ttl - This parameter specifies the
	    number of VRRPv2 packets with TTL errors. Default value is 0,
	    monitoring can be turned on by specifying value 1

	7.  advertise\_recv\_with\_invalid\_type - This parameter specifies the
	    number of received VRRPv2 packets of invalid type. Default value
	    is 0, monitoring can be turned on by specifying value 1

	8.  ip\_address\_owner\_conflicts - This parameter specifies the number
	    of VRRPv2 packets with ip address owner conflicts. Default value
	    is 0, monitoring can be turned on by specifying value 1

	9.  mismatched\_addr\_list\_pkts - This parameter specifies the number
	    of VRRPv2 packets with incorrect virtual IP address lists. Default
	    value is 0, monitoring can be turned on by specifying value 1

	10. mismatched\_auth\_type\_pkts - This parameter specifies the number
	    of VRRPv2 packets with a non-matched authentication mode.. Default
	    value is 0, monitoring can be turned on by specifying value 1

	11. near\_failovers - This parameter specifies the Number of Near
	    Failovers statistic. Default value is 0, monitoring can be turned
	    on by specifying value 1

	12. other\_reasons - This parameter specifies the Number of other
	    errors statistics. Default value is 0, monitoring can be turned on
	    by specifying value 1

- 'Policy Constructor' defines Monitor Resource URI. This script
specifies monitoring uri's to monitor the following:

	1.  VRRPv2 Advertisement packets are sent at an incorrect interval count

	2.  VRRPv2 Advertisement packets are received in init state count
	
	3.  VRRPv2packets with invalid length count

	4.  VRRPv2 packets with TTL errors count

	5.  VRRPv2 packets of invalid type count

	6.  VRRPv2 packets with ip address owner conflicts count

	7.  VRRPv2 packets with incorrect virtual IP address lists count

	8.  VRRPv2 packets with a non-matched authentication mode count

	9.  VRRPv2 Near Failovers statistics count

	10. VRRPv2 errors statistics count

This monitored data is then plotted in a time-series chart for
analysis purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA