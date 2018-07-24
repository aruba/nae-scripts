#### Script File Name: stp\_health\_monitor.1.0.py

### SUMMARY
The purpose of this script is to monitor the health of STP port.  

### PLATFORMS SUPPORTED
- 8400X
- 8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

The script defines Monitor Resource URI(s), Monitor condition and Action :

Note: The monitored data is plotted in a time-series chart for analysis purpose.

### SCRIPT DESCRIPTION
The main components of the script are Manifest, Parameter Definitions and python code.  

#### 'Manifest' defines the unique name for this script.
#### 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters:
1. tcn_upper_threshold - Upper threshold for rate of topology change count per second.
2. tcn_lower_threshold - Lower threshold for rate of topology change count per second.
#### Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
1. Rate of topology change count for STP instance over 10 seconds.
2. Rate of STP port BPDU transmit packets over 10 seconds.
3. Rate of STP port BPDU receive packets over 10 seconds.
4. STP port state
5. STP port role
6. STP port inconsistent loop guard
7. STP port inconsistent root guard
8. Rate of STP port forward transition count over 10 seconds.
#### Conditions:  This script specifies monitoring condition as following:
1. STP port state, port role and port inconsistent loop guard/root guard are in invalid combination.
2. Rate of STP topology change count is greater than the upper threshold.
3. Rate of STP topology change count is less than or equal to the lower threshold.
4. Rate of BPDU receive packets over 10 seconds is less than 0.1, for Root port role and Forwarding port state.
5. Rate of BPDU receive packets over 10 seconds is less than 0.1, for Alternate port role and Blocking port state.
6. Rate of BPDU transmit packets over 10 seconds is less than 0.1 for Designated port role and Forwarding port state.
7. Rate of forward transition count over 10 seconds is greater then 0, for Root port role and Forwarding port state.
8. Rate of forward transition count over 10 seconds is greater than 0, for Designated port role and Forwarding port state.

#### Actions:  This script specifies monitoring action as following:  

- When monitoring condition (1) is hit, the agent status is changed to Critical. CLI commands to show spanning-tree detail, show spanning-tree mst <instance> detail, show spanning-tree mst-config and show spanning-tree mst are executed.
- When monitoring condition (2) is hit, the agent status is changed to Critical. CLI commands to show spanning-tree detail, show spanning-tree mst <instance> detail are executed.
- When monitoring condition (3) is hit, the agent state is changed to normal.
- When monitoring condition (4), (5) or (6) is hit, the agent status is changed to Critical. CLI commands to show spanning-tree detail, show spanning-tree mst and show copp statistics are executed.
- When monitoring condition (7) or (8) is hit, the agent status is changed to Critical. CLI command to show spanning-tree mst detail is executed.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
