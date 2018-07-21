#### Script File Name: daemon\_resource\_monitor.2.0.py

### SUMMARY
The intent of this script is to monitor CPU and Memory utilization (in percentage) of top 4 (configurable) system daemons for all switch's subsystems and management modules against a specified threshold in a time window.  Default CPU/Memory threshold value in script is 90%. Default time interval is 30 seconds. Default top 4 daemons as parameters in script are 'ops-switchd', 'ovsdb-server', 'hpe-routing' and 'arpmgrd'.

If any of the monitored system daemon CPU/Memory utilization exceeds configured CPU/Memory threshold continuously for the configured time interval, agent generates Critical alert and logs corresponding daemon system resource utilization details in Syslog.

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.000X

### SCRIPT DESCRIPTION
The important sections of System Daemon Resource Monitoring script are 'Manifest', 'ParameterDefinitions' and the actual python code.  The ’Manifest’ section defines the unique name for this script with short description about script purpose.  'ParameterDefinitions' section defines script parameters. In this case, 4 system daemon names, CPU/Memory threshold value and time interval to consider continuous CPU/Memory utilization against thresholds.  

The script handles the main logic for monitoring CPU/Memory utilization of 4 system daemons against CPU/Memory threshold for the time interval and actions on exceeding threshold values. CPU/Memory utilization of 4 system daemons will be presented to the user in a time series chart. Time series chart can present at most 8 monitors (daemon CPU/Memory utilization). User can select daemon monitors (CPU and Memory) that need to be presented in agent graph using customization feature. Conditions are defined to check CPU/Memory utilization against corresponding CPU/Memory threshold of each given daemon for the given time interval. When the CPU/Memory threshold is exceeded by any daemon, below actions are taken by the agent 

- Agent status is set to Critical. 

- Syslog message indicating the daemon that exceeded configured CPU/Memory threshold. 

- CLI - 'show system resource-utilization daemon <daemon>' to capture daemon CPU, Memory and File descriptor utilization details. 

Agent alerts about each CPU/Memory threshold exceeding for each monitored daemon. Each CPU/Memory threshold condition has a 'clear action' defined which alerts about daemon coming back to normal CPU/Memory utilization from high utilization. 

Note: Dynamic parameter changes i.e. after agent creation, are not supported for this script. 

Note: The value of the CPU utilization shown (as a percentage) is the sum of utilization across all the CPU cores in the system. For example, if the daemon uses 4 cores at 30% each, the CPU monitor shows a value of 120%. There may be a difference in the displayed CPU utilization value between NAE and CLI. NAE is displaying the last value in 5 seconds intervals whereas CLI displays the value at the time of command execution. 

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
