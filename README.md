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
- [Repository Links](#repo_links)
- [Repository Structure](#repo_structure)

------------------------------------------------------------------------------

<a id='repo_links'></a>
#### Repository Links:

------------------------------------------------------------------------------
The GitHub repository will be a part of the “aruba” organization on GitHub: 

https://github.com/aruba/nae-scripts

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
	├── LICENSE.md
	├── README.md
	└── Release-Notes
</pre>

Inside each folder, you will find the actual script and the documentation 
around that script: 
<pre>
	├── interface_state_stats_monitor.1.0.md
	└── interface_state_stats_monitor.1.0.py
</pre>


- #### license: 
	Apache 2.0 license file

- #### README:
	How to use this repository 

- #### Release-Notes:
	version by version notes for agents on the repository. 
	Known issues, Fixed issues etc.
