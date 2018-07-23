#### Script File Name: line\_card\_monitor.1.0.py

Script Functionality Guide for Monitoring Line Cards on the 8400x switch 

==============================================================================

### Contents
------------------------------------------------------------------------------
- [Overview](#Overview)
- [Prerequisites](#Prerequisites)
- [Use Case(s)](#Use_Case)
- [Functional Description](#Functional_Description)
- [Platform(s) Tested](#Platform_Tested)
- [Error-Handling](#Error-Handling)

<a id='Overview'></a>
#### Overview:

------------------------------------------------------------------------------
The intent of this script is to monitor health of all the Line cards (LC) 
on the switch. Agent monitors line card state, CPU and Memory utilization. 
In case, any line card is down, agent collects corresponding line card logs 
by executing switch CLI/Shell commands which help to know the cause of line 
card failure  
 
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

Listed below are the high level use case for Line Card monitoring on 
8400x switch:     

"As an Administrator, I would like to monitor all the Line Card (LC) state,
CPU/Memory utilization on the switch, collect line card logs in case there is
a line card failure to know the cause and each line card state, CPU and Memory
utilization to be represented in a time-series chart for analysis purpose."    
   
<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main sections of System Daemon Resource Monitoring script are 'Manifest',
'ParameterDefinitions' and the 'Policy Constructor'.

- The ’Manifest’ section defines the unique name for this script with short
description about script purpose.
- 'ParameterDefinitions' section defines script parameters. In this case,
there are no parameters.   
- The 'Policy Constructor' handles the main logic for monitoring state,
CPU/Memory utilization of all line cards on the switch. State, CPU and Memory
utilization of all line cards will be presented to the user in single time 
series chart. User can customize the chart to select the line card monitors 
that needs to be presented since max monitors that are presented are 8. 
Single condition is defined to check whether any line card is in 'down' state. 
If any line card is in 'down' state, below actions are taken by the agent:
	- Agent status is set to Critical. 
	- Details of line card which is in down state are logged to Syslog.
	- Below CLI or Shell commands are executed to collect line card logs to know
	cause of failure.
		- CLI - 'show mod <lc_slot>'  
		- CLI - 'show events -d hpe-cardd' 
		- Shell - 'ovs-appctl -t hpe-cardd fastlog show lc <lc_number>' 
 
Agent alerts for each and every line card failure on the switch. Also Agent
generates clears earlier alert in case line card comes back from 
'failed' or 'down' state. 
 
<a id='Platform_Tested'/></a>
#### Platform(s) Tested:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------ 
- In case, if initial 8 default monitors that are rendered in agent graph are 
not as per user liking, user has option to customize monitors that are 
preferred (max 8). 
