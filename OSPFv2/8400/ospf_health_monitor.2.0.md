#### Script File Name: ospf\_health\_monitor.2.0.py

### SUMMARY
The purpose of this script is to detect an anomaly in OSPF protocol. It monitors the ifsm_state of all the OSPF interfaces and various OSPF interface statistics for further troubleshooting.   

### MINIMUM SOFTWARE VERSION(S) REQUIRED
ArubaOS-CX XL/TL.10.01.000X

### SCRIPT DESCRIPTION
The main components of the script are Manifest, Parameter Definitions and the actual python code.  

'Manifest' defines the unique name for this script.
The script defines Monitor Resource URI, Monitor condition and Action: 

#### Monitors:   

OSPFv2 Interface state machine. 

#### Conditions: This script specifies monitoring condition:  

ifsm_state (state machine) following state changes:
1. change from bdr to down 
2. change from bdr to point to point
3. change from dr to down 
4. change from dr to point to point 
5. change from dr other to down
6. change from dr other to point to point 
7. change from bdr to waiting
8. change from dr other to waiting 
9. change from dr other to waiting 
10. change from down to bdr 
11. change from waiting to bdr 
12. change from point to point to bdr 
13. change from bdr to dr  
14. change from bdr to dr other 
15. change from down to dr 
16. change from waiting to dr 
17. change from point to point to dr 
18. change from dr to bdr 
19. change from dr to dr other 
20. change from down to dr other 
21. change from waiting to dr other 
22. change from point to point 
23. change from dr other to bdr 
24. change from dr other to dr

OSPFv2 Interface Statistics:
1. state_changes - Rate of lsa_checksum_sum greater than 0.03 over a period of 10 seconds.
2. rcvd_invalid_checksum - Rate of lsa_checksum_sum greater than 0 over a period of 10 seconds.
3. rcvd_bad_lsa_length - Rate of lsa_checksum_sum greater than 0 over a period of 10 seconds.
4. rcvd_bad_lsa_checksum - Rate of lsa_checksum_sum greater than 0 over a period of 10 seconds.
5. rcvd_bad_lsa_data - Rate of lsa_checksum_sum greater than 0 over a period of 10 seconds.
6. lsa_checksum_sum - Rate of lsa_checksum_sum greater than 0 over a period of 10 seconds.
 

Actions: This script specifies  monitoring action as following:  

Critical alert (ifsm_state)– When the monitoring condition  specified above (OSPFv2 ifsm_state) numbered [1, 9]  are hit, 'critical' action is taken. In this action agent is marked as critical and CLI command (show ip ospf interface {ospf_interface} all-vrfs) is executed and detailed impact analysis of lost/found OSPFv2 routes and OSPFv2 neighbors is done. This Impact Analysis reports is shown as custom report in the monitoring agent UI. 

Critical alert (OSPF_Interface Statistics) - The monitoring condition specified above (OSPFv2 Interface Statistics) is hit, 'critical' action is taken. In this action agent is marked as critical and CLI command (show ip ospf interface {ospf_interface}) is executed. The CLI output is shown on the monitoring agent UI.

Normal alert (ifsm_state) -  When the monitoring condition  specified above (OSPFv2 ifsm_state) numbered [10, 24] are hit, 'normal' action is taken. In this action script is marked as Normal and CLI command (show ip ospf interface {ospf_interface} all-vrfs) is executed and detailed impact analysis of lost/found OSPFv2 routes and OSPFv2 neighbors. This Impact Analysis reports is shown as custom report in the monitoring agent UI.

Normal alert (OSPF_Interface Statistics) - The monitoring condition specified above (OSPFv2 Interface Statistics) is hit, 'normal' action is taken. In this action agent is marked as normal and CLI command (show ip ospf interface {ospf_interface}) is executed. The CLI output is shown on the monitoring agent UI.
This monitored data is then plotted in a time-series chart for analysis purpose. 

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
