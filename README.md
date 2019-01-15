------------------------------------------------------------------------------

### Overview

------------------------------------------------------------------------------

Aruba Network Analytics Engine Scripts are troubleshooting solutions that 
allow the administrator to monitor data of a specific resource
(protocol/system) and capture time series snapshot of various possible
states that this resource can transition to.

The administrator creates scripts that are based on NAE framework. A script 
indicates what data should be monitored, specifies conditions which act as 
triggers on the monitored data, specifies pre-defined actions 
(e.g. syslog, cli commands, etc) that can be executed when the condition is
met, or indicate callback actions which are nothing but python functions to
be executed when the condition is met.

Once the Network Analytics Script is uploaded and instantiated, Time Series
data collection will begin, based on the data that is monitored. The 
administrator views Time Series data associated with Network Analytics Agents
as charts on the Web UI.

------------------------------------------------------------------------------

### Contents

------------------------------------------------------------------------------
- [Repository Structure](#repo_structure)

------------------------------------------------------------------------------

<a id='repo_structure'></a>
#### Repository Structure:

------------------------------------------------------------------------------
Structure of the “nae-scripts” repository is as shown below
<pre>
	├── common
	├── 8400
	├── 832X
	├── genericx86
	├── README.md
</pre>

Inside each folder, the user will find another folder that contains scripts and 
documentation that are published (or available to download): 
<pre>
	├── interface_state_stats_monitor.1.0.md
	└── interface_state_stats_monitor.1.0.py
</pre>

- #### README:
	How to use this repository 

