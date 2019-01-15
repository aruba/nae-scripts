#### Script File Name: interface\_tx\_rx\_stats\_monitor.1.0.py

Script Functionality Guide for monitoring Interface packets statistics

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

This Interface Tx/Rx Stats Monitor script is intended to monitor the number of
packets being transmitted or received and the packets dropped while 
transmitting on a interface. This script monitors all interfaces of the 
switch. 8400 is an aggregation/core switch, and it is necessary to create an
easy monitoring mechanism on interfaces so that the time series chart serves 
for visualization of port level errors. 
 
A point to note is that when the interface goes down, these counters are not 
reset or brought back to zero. No change in counters across any of the 
monitored aspects indicate that the port is either operationally down or has 
been administratively shut down. 
 
The underlying root cause for drops may be congestion or may be link 
failures/flaps, and this script does not really get to the actual root cause,
but serves for quick visualization. 

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

Listed below are the high level use case for Monitoring Interface Tx/Rx
packets Stats of the Switch:

"As an administrator I would like to view and monitor the number of
packets being transmitted or received and the packets dropped while
transmission or reception on all interfaces. I should be able to view the
count of packets being transmitted, received and dropped information on
the graph.”

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of Interface Tx/Rx monitor script are Manifest and
the Policy Constructor.

- The 'Manifest' defines the unique name for this script. 

- The 'Policy Constructor' handles the main logic for monitoring the Tx/Rx 
packets transmitted and dropped for a given interface.  

The script does not have any Rules or Thresholds since they are fully trusted
to be handled by the switch inherently. 

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
N/A
