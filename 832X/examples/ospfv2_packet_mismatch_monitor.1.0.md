#### Script File Name: ospfv2\_packet\_mismatch\_monitor.1.0.py

Script Functionality Guide for Monitoring OSPF2 Packet Mismatch

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

This OSPF2 Packet Mismatch Count monitor script is intended to monitor
OSPFv2 interface statistics related to invalid, error or mismatch
packet count for specified VRF name , OSPFv2 process id, OSPFv2 area
id and OSPFv2 interface in the system.

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

Listed below are the high level use cases for OSPF2 Packet Mismatch
Count monitoring on 8320 Switches:

As an Administrator, I would like to monitor

	1.  Number of times OSPFv2 Area Mismatch packets are seen.
	2.  Number of times OSPFv2 Authentication Errors packets are seen.
	3.  Number of times OSPFv2 Authentication Fail packets are seen.
	4.  Number of times OSPFv2 Authentication Mismatch packets are seen.
	5.  Number of times OSPFv2 Bad LSA Checksum packets are seen.
	6.  Number of times OSPFv2 Bad LSA Data packets are seen.
	7.  Number of times OSPFv2 Bad LSA Length packets are seen.
	8.  Number of times OSPFv2 Bad LSA Type packets are seen.
	9.  Number of times OSPFv2 Bad LSU Length packets are seen.
	10. Number of times OSPFv2 Bad Hello packets are seen.
	11. Number of times OSPFv2 Dead Interval Mismatch packets are seen.
	12. Number of times OSPFv2 Hello Interval Mismatch packets are seen.
	13. Number of times OSPFv2 Invalid Protocol Version packets are seen.
	14. Number of times OSPFv2 Net Mask Mismatch packets are seen.
	15. Number of times OSPFv2 MTU Mismatch packets are seen.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script uses
the following name:

ospfv2\_packet\_mismatch\_monitor
 
- 'Parameter Definitions' defines the input parameters to the script.
This script requires the following parameters:

	1.  vrf\_name – This parameter specifies VRF unique name. Default value
    is default

	2.  ospf\_process\_id - This parameter specifies the OSPFv2 unique
    process id. Default value is 1

	3.  ospf\_area\_id - This parameter specifies the OSPFv2 unique router
    area id. Default value is 0.0.0.0

	4.  ospf\_interface\_id - This parameter specifies the OSPFv2 unique
    router interface. Default value is 1/1/1

	5.  area\_mismatch - This parameter specifies Number of times OSPFv2
    Area Mismatch packets are seen. Default value is 0, monitoring can
    be turned on by specifying value 1

	6.  auth\_errors - This parameter specifies Number of times OSPFv2
    Authentication Errors packets are seen. Default value is 0,
    monitoring can be turned on by specifying value 1

	7.  auth\_fail - This parameter specifies the numberof times OSPFv2
    Authentication Fail packets are seen. Default value is 0,
    monitoring can be turned on by specifying value 1

	8.  auth\_mismatch - This parameter specifies the numberof times OSPFv2
    Authentication Mismatch packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	9.  bad\_lsa\_checksum - This parameter specifies the numberof times
    OSPFv2 Bad LSA Checksum packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	10. bad\_lsa\_data - This parameter specifies the numberof times OSPFv2
    Bad LSA Data packets are seen.Default value is 0, monitoring can
    be turned on by specifying value 1

	11. bad\_lsa\_length - This parameter specifies the numberof times
    OSPFv2 Bad LSA Length packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	12. bad\_lsa\_type - This parameter specifies the numberof times OSPFv2
    Bad LSA Type packets are seen.Default value is 0, monitoring can
    be turned on by specifying value 1

	13. bad\_lsu\_length - This parameter specifies the numberof times
    OSPFv2 Bad LSU Length packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	14. bad\_hello - This parameter specifies the numberof times OSPFv2 Bad
    Hello packets are seen.Default value is 1, monitoring can be
    turned off by specifying value 0

	15. dead\_mismatch - This parameter specifies the numberof times OSPFv2
    Dead Interval Mismatch packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	16. hello\_mismatch - This parameter specifies the numberof times OSPFv2
    Hello Interval Mismatch packets are seen.Default value is 0,
    monitoring can be turned on by specifying value 1

	17. invalid\_version - This parameter specifies the numberof times
    OSPFv2 Invalid Protocol Version packets are seen.Default value is
    0, monitoring can be turned on by specifying value 1

	18. mask\_mismatch - This parameter specifies the numberof times OSPFv2
    Net Mask Mismatch packets are seen. Default value is 0, monitoring
    can be turned on by specifying value 1

	19. mtu\_mismatch - This parameter specifies the numberof times OSPFv2
    MTU Mismatch packets are seen. Default value is 0, monitoring can
    be turned on by specifying value 1

- 'Policy Constructor' defines Monitor Resource URI. This script
specifies monitoring uri to monitor the following:

	1.  OSPFv2 Area Mismatch packet count
	2.  OSPFv2 Authentication Errors packet count
	3.  OSPFv2 Authentication Fail packet count
	4.  OSPFv2 Authentication Mismatch packet count
	5.  OSPFv2 Bad LSA Checksum packet count
	6.  OSPFv2 Bad LSA Data packet count
	7.  OSPFv2 Bad LSA Length packet count
	8.  OSPFv2 Bad LSA Type packet count
	9.  OSPFv2 Bad LSU Length packet count
	10. OSPFv2 Bad Hello packet count
	11. OSPFv2 Dead Interval Mismatch packet count
	12. OSPFv2 Hello Interval Mismatch packet count
	13. OSPFv2 Invalid Protocol Version packet count
	14. OSPFv2 Net Mask Mismatch packet count
	15. OSPFv2 MTU Mismatch packet count

This monitored data is then plotted in a time-series chart for
analysis purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

NA
