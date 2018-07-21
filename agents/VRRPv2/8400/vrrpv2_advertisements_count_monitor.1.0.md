#### Script File Name: vrrpv2\_advertisements\_count\_monitor.1.0.py

### SUMMARY
This VRRPv2 Advertisements Count monitor script is intended to monitor VRRPv2 statistics related to advertisements (Sent/Received) and  zero priority (Sent/Received) packet count for the specified VRRP ID and interface in the system. The interface name can be a physical, vlan or lag interface. 

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.000X

### CONFIGURATION NOTES
The main components of the script are Manifest, Parameter Definitions and the Policy Constructor.   

#### 'Manifest' defines the unique name for this script. This script specifies the following name: vrrpv2_advertisements_count_monitor 


#### 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 

1. vrrp_id – This parameter specifies VRRPv2 instance unique id. Default value is 1 

2. port_name - This parameter specifies the interface that this agent will monitor for any VRRP state changes. This can be a physical, vlan or lag interface. Default value is 1/1/1 

#### 'Policy Constructor' defines Monitor Resource URI. This script specifies monitoring uri's to monitor the following:  

1. VRRPv2 advertisement Tx Packets 

2. VRRPv2 advertisement Rx Packets 

3. VRRPv2 zero priority Tx Packets 

4. VRRPv2 zero priority Rx Packets 

This monitored data is then plotted in a time-series chart for analysis purpose. 

### PLATFORM(S) TESTED
8400x

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
