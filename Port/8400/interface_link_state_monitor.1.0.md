#### Script File Name: interface\_link\_state\_monitor.1.0.py

Script Functionality Guide for monitoring link state in the system.

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

This interface link state monitor script is intended to monitor link state 
change happening on any interface in the system. This is the observed state of
the physical network link. Link's carrier status can be either "up" or "down".

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

Listed below are the high level use case for monitoring link state change 
happening of the Switch:

"As an administrator I would like to view and monitor link state change 
happening on any interface in my switch. I should be able to view the state 
change information on the graph and get alerts if an interface link state 
changes from "up" to "down".

<a id='Functional_Description'/></a>
#### Functional Description:

------------------------------------------------------------------------------

The main components of interface link state monitor script are Manifest and 
the Policy Constructor.

- The 'Manifest' defines the unique name for this script.

- The 'Policy Constructor' handles the main logic for monitoring the link 
state change happening on any interface in the system.

Condition is defined to monitor 'link\_state' of all interfaces. 'link\_state'
specifies the Link's carrier status of an interface. If the link state of an
interface transitions from "up" to "down" then the following actions are 
taken:

- Agent status is set to Critical.

- Syslog messages is written indicating that the link state of an interface 
is gone down.

If the link state of all enabled interfaces comes back to the "up" state then
the agent status is set back to Normal.

<a id='Platforms_Supported'/></a>
#### Platform(s) Supported:

------------------------------------------------------------------------------
This script has been tested on platforms 8400x.

<a id='Error-Handling'/></a>
#### Error Handling:

------------------------------------------------------------------------------
N/A
