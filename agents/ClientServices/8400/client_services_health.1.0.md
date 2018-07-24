#### Script File Name: client\_services\_health.1.0.py

### SUMMARY
The purpose of this script is to monitor the DHCP ratio of DHCP client requests to DHCP server responses for further troubleshooting.   

### PLATFORM(S) SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

### SCRIPT DESCRIPTION
The main components of the script are Manifest, Parameter Definitions and python code.  

'Manifest' defines the unique name for this script.
'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters:
DHCP_Server_IP – This parameter specifies the IP address of the DHCP server. Default value is 0.0.0.0
The script defines Monitor Resource URI(s), Monitor condition and Action :

#### Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
Number of valid IPv4 DHCP relay requests processed.

Number of valid IPv4 DHCP relay responses processed.

Note: The monitored data is plotted in a time-series chart for analysis purpose.  

#### Conditions:  This script specifies monitoring condition as following:
DHCP Ratio of DHCP client requests to DHCP server responses greater than 1.1 for a time period of 60 seconds.
DHCP Ratio of DHCP client requests to DHCP server responses less than or equal to 1.1 for a time period of 60 seconds.

#### Actions:  This script specifies  monitoring action as following:  

Critical alert – The monitoring condition (1) specified is hit, the monitoring action 'critical' is taken. In this action, agent is marked as critical, CLI show dhcp-relay is executed, result of DHCP server is ping is displayed and syslog is generated displaying the anomaly ratio value. The CLI outputs and the syslog is shown in the monitoring agent UI.

Normal alert -  The monitoring condition (2) specified is hit, the monitoring action 'normal' is taken. In this action agent is marked as Normal and a syslog is generated indicating the DHCP ratio is back to normal. This syslog is shown in the monitoring agent UI.


### LICENSES
Apache License, Version 2.0

### REFERENCES
http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine
