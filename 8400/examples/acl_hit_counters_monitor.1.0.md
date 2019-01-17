#### Script File Name: acl\_hit\_counters\_monitor.py

Script Functionality Guide for Monitoring ACL Hit Counters

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
This ACL Hit Counters monitoring script is intended to monitor the hit 
counters for a configured ACL rule with a given ACE Id.

<a id='Prerequisites'></a>
#### Prerequisites:
-----------------------------------------------------------------------------
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

----------------------------------------------------------------------------
Listed below are the high level use cases for ACL hit counters monitoring on 
8400X switch:

"As an Administrator, I would like to monitor the Hit Counters for a 
configured ACL rule having the specified ACE Id. The monitored counters 
will be represented in a time-series chart for analysis purpose."

<a id='Functional_Description'/></a>
#### Functional Description:

-----------------------------------------------------------------------------
The main sections of the ACL hit counters script are 'Manifest',
'ParameterDefinitions' and the 'Policy Constructor'.

The ’Manifest’ section defines the unique name for this script with short 
description about script purpose. 'ParameterDefinitions' section defines 
script parameters in this case - port number and the ACE number/Id. Port 
number is any valid string value as configured in the 8400x switch. ACE
number/Id is any valid Integer number that the administrator provides
as a unique sequence number when applying the ACL rules on the port
or interface.

The 'Policy Constructor' handles the main logic for monitoring the ACL
Hit counters values. A single monitor condition has been defined to
monitor the ACL hit counters on the 8400x switch. There are no actions
or call backs alerts associated with this monitor condition. 
The monitored values are directly plotted on the time series charts 
available in the the WEB-UI for analysis purpose.  

Note: Dynamic parameter changes I.e. after agent creation, are not supported
for this script.

<a id='Platform_Tested'/></a>
#### Platform(s) Tested:

------------------------------------------------------------------------------
This script has been tested on 8400X switch.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------

- Ensure to provide the right port number of the 8400x switch on which the ACL 
  rule was applied.
- Ensure to provided the valid ACE Id (Integer number) which the administrator 
  provided while configuring the ACL rules on the 8400x switch.
