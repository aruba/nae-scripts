#### Script File Name: lag\_status\_monitor.1.0.py

Script Functionality Guide for Monitoring Status of configured LAG:

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

This Lag Status Monitor script is intended to monitor the overall status
of configured LAG.

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

Listed below are the high level use case for Monitoring Lag Status of
the Switch:

"As an Administrator, I would like to monitor overall status of the
configured LAG. I should be able to view the LAG status change
information on the graph and get alert(s) when the configured LAG goes
down "

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of Lag status monitor script are Manifest,
ParameterDefinitions and the Policy Constructor.

- The 'Manifest' defines the unique name for this script.
- 'ParameterDefinitions' section defines the following script parameters
	- lag\_id/name -&gt; specifies the LAG id to be monitored as a 
	parameter from user. 
- The 'Policy Constructor' handles the main logic for monitoring the status of
LAG.

Conditions are defined to verify the transition of forwarding state of 
configured LAG from "true" to "false" and blocking layer to "AGGREGATION".
When the specific Condition is met a detailed Syslog message indicating the 
transition states and output of CLI command ('show lacp aggregate {lag\_id}')
is displayed  in Alert Window and the policy Status is changed to Critical. 
When Blocking layer and forwarding state is transitioned back to "NONE" and 
"true" respectively, then the policy status is set back to 'Normal'.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8320.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure that the given LAG ID/Name is valid.

- Ensure that the chosen LAG for monitoring is properly configured.

- If a LAG which is not configured is given as a parameter then script
will throw "invalid URI error".

- If user configures the LAG after agent instantiation then user has to
disable and enable the agent to start monitoring the LAG status.
