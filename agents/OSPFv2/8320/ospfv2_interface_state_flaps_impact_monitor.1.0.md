#### Script File Name:
ospfv2\_interface\_state\_flaps\_impact\_monitor.1.0.py

Script Functionality Guide for Monitoring OSPFv2 Interface State Flaps
Impact Analysis

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

This OSPFv2 Interface State Flap monitor script is intended to monitor
OSPFv2 interface state flaps on a specified interface and provide impact
analysis on OSPFv2 routes and OSPFv2 neighbors.

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

Listed below is the high level use cases for OSPFv2 interface state flap
on a specified interface.

monitoring on 8400x Switches:

As an Administrator, I would like to monitor specified OSPFv2 interface
state flap to predict any instability in the OSPF network by analyzing
impacted OSPFv2 routes and OSPFv2 neighbors.

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the script are Manifest, Parameter Definitions
and the Policy Constructor.

- 'Manifest' defines the unique name for this script. This script uses the
following name:

	- ospfv2\_interface\_state\_flap\_impact\_analysis

- 'Parameter Definitions' defines the input parameters to the script. This
script requires the following parameters:

	- vrf\_name – This parameter specifies VRF unique name. Default value 
	is "default"

	- ospf\_process\_id - This parameter specifies the OSPFv2 unique 
	process id. Default value is 1

	- ospf\_area\_id - This parameter specifies the OSPFv2 unique router 
	are id. Default value is 0.0.0.0

	- ospf\_interface\_id - This parameter specifies the OSPFv2 unique 
	router interface. Default value is 1/1/1

- 'Policy Constructor' defines Monitor Resource URI, Monitor condition and
Action.

A.  This script specifies monitoring URI to monitor the following:

    1.  OSPFv2 Interface state machine.

<!-- -->

A.  This script specifies monitoring condition as following:

    1.  OSPFv2 interface state machine change from bdr to down

    2.  OSPFv2 interface state machine change from down to bdr

    3.  OSPFv2 interface state machine change from waiting to bdr

    4.  OSPFv2 interface state change from bdr to dr

    5.  OSPFv2 interface state machine change from dr to down

    6.  OSPFv2 interface state machine change from down to dr

    7. OSPFv2 interface state machine change from waiting to dr

    8. OSPFv2 interface state machine change from dr other to down

    9. OSPFv2 interface state machine change from down to dr other

    10. OSPFv2 interface state machine change from waiting to dr other

    11. OSPFv2 interface state machine change from point to point

    12. OSPFv2 interface state change from dr other to bdr

    13. OSPFv2 interface state change from dr other to point to point

    14. OSPFv2 interface state change from dr other to dr

    15. OSPFv2 interface state change from bdr to waiting

    16. OSPFv2 interface state change from dr other to waiting

    17. OSPFv2 interface state change from dr other to waiting

A.  This script specifies monitoring action as following:

    1.  Normal alert - The monitoring condition specified above numbered
        2, 3, 4, 6, 7, 9, 10, 11, 12 and 14 when
        hits, the monitoring action 'normal' is taken. In this action
        script is marked as Normal and CLI show ip ospf interface is
        executed and detailed impact analysis of lost/found OSPFv2
        routes and OSPFv2 neighbors. This Impact Analysis reports is
        shown as custom report in the monitoring agent UI

    2.  Critical alert – The monitoring condition specified above
        numbered 1, 5, 8, 13, 15, 16, and 17 when hits, the
        monitoring action 'critical' is taken. In this action script
        is marked as critical and CLI show ip ospf interface is
        executed and detailed impact analysis of lost/found OSPFv2
        routes and OSPFv2 neighbors is done. This Impact Analysis
        reports is shown as custom report in the monitoring agent UI.

  

 Example of Custom report showing Impact Analysis of Routes and
 Neighbors on interface state change is given below-

  

 **Interface 1/1/1 Interface state machine changed from Backup DR to 
 Down**

 **OSPF Route Analysis Route Event Report – Thu Aug 24 08:14:15**

 \_ \_ \_ \_ \_ \_ \_ \_\_ \_ \_ \_\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_
 \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_
 \_ \_ \_ \_ \_

 | **Route Prefix** | **Route Via** | **Route Type** | **Event**

------------------------------------------------------------------------------

 | 10.10.10.0/24 | Via 10.10.10.2 interface 1/1/1 | Intra Area | Route
 has been learnt

 | 30.30.30.0/24 | Via 20.20.20.3 interface 1/1/3 | Intra Area | Route
 has been removed

------------------------------------------------------------------------------

 **OSPF Route Analysis Route Event Report – Thu Aug 24 08:14:15**

 \_ \_ \_ \_ \_ \_ \_ \_\_ \_ \_ \_\_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_
 \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_
 \_ \_ \_ \_ \_

 | **Neighbor** | **Router ID** | **State** | **DR** | **BDR** |
 **Event**

------------------------------------------------------------------------------

 | 10.10.10.2 | 192.168.1.1 | FULL | 10.10.10.2 | 10.10.10.1 | Neighbor
 has been formed

 | 30.30.30.1 | 172.154.1.2 | FULL | 30.30.30.2 | 30.30.30.1 | Neighbor
 has been removed

------------------------------------------------------------------------------

This monitored data is then plotted in a time-series chart for analysis
purpose.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on 8400X switch.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
NA
