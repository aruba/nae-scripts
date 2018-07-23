#### Script File Name: stp\_bpdu\_tcn\_rate\_monitor.1.0.py
Script Functionality Guide for Monitoring the STP BPDU Counters and the
Topology Change Notification (TCN) Rate:

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

The STP BPDU and TCN rate script is intended to monitor the STP BPDU
Counters and the Topology Change Notifications (TCN) and raise an alert
if the rate of TCN exceeds a certain threshold value for a specified
time.

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

Listed below are the high level use case for Monitoring the Spanning
tree BPDU count and the rate of TCN:

"As an Administrator, I would like to monitor the rate of topology
change notification to determine the stability of the network, the STP
BPDU Counters to know the performance of Spanning Tree Protocol"

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of STP BPDU and TCN rate script are Manifest,
ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script and
- 'ParameterDefinitions' has four parameters that are intended to be
entered by the user

	- stp\_instance\_id – the ID of STP instance to be monitored

	- tcn\_upper\_threshold – the threshold value of rate of TCN beyond 
	which the network state is said to be critical

	- tcn\_lower\_threshold - the threshold value of rate of TCN below 
	which the network state is said to be normal

	- stp\_port – the port that involved in spanning tree for which the 
	BPDU counters needs to be monitored

The 'Policy Constructor' handles the main logic for monitoring the rate
of TCN and BPDU counters

Conditions are defined to compare the rate of TCN value over a period of
10 seconds with the entered threshold value. When the monitored rate
value exceeds the upper threshold value, a detailed Syslog message
indicating the rate exceeding the threshold value and output of CLI
command ('show spanning-tree detail') and ('show spanning-tree mst
{stp\_instance\_id} detail') is displayed in Alert Window and the policy
Status is set to Critical. When the rate of TCN falls below the lower
threshold value, then the policy status is set back to 'Normal'.

The agent chart displays the BPDU counters value. This information can
be used to monitor the performance of the STP.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------

This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure that the entered STP Instance ID for monitoring rate of TCN is
properly configured.

- Ensure that the entered Port number for monitoring BPDU counters is
properly configured.

- Ensure while giving the TCN Upper and Lower Threshold as it is the
rate value over a period of 10 seconds and not the absolute TCN value
