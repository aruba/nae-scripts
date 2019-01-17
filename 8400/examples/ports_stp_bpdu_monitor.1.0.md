#### Script File Name: ports\_stp\_bpdu\_monitor.1.0.py

Script Functionality Guide for Monitoring BPDU sent vs received on all
STP configured ports:

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

This Ports STP BPDU Monitor script is intended to monitor the BPDU sent vs 
received on all STP configured ports.

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

Listed below are the high level use case for Monitoring BPDU sent vs
received:

"As an Administrator, I would like to monitor the BPDU sent vs
received on all STP configured ports to know the performance of spanning
tree protocol ".

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of the "ports\_stp\_bpdu\_monitor" script are
Manifest and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- The 'Policy Constructor' handles the main logic for monitoring the 'BPDU
sent vs received' for all STP configured ports. 

There are no conditions for the monitored BPDU counters. The default STP mode 
is MSTP.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

N/A
