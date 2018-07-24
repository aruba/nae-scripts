#### Script File Name: vrrpv2\_transitions\_monitor.1.0.py

### SUMMARY
This script monitors VRRPv2 statistics related to state transition count for the given VRRP ID and interface in the system. The VRRP can be in one of the following states: Init, Master, Back up. The interface name can be a physical, van or lag interface.

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CXXL/TL.10.01.000X

### CONFIGURATION NOTES
The main components of the script are Manifest, Parameter Definitions and the Policy Constructor.   

#### 'Manifest' defines the unique name for this script. This script uses the following name: vrrp_state_transition_monitor 

#### 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 

##### vrrp_id – This parameter specifies VRRPv2 instance unique id.  

##### port_name - This parameter specifies the interface that this agent will monitor for any :xVRRP state  changes. This can be a physical, vlan or lag interface. 


#### 'Policy Constructor' defines Monitor Resource URI. This script specifies monitoring URI's to monitor the following:  

1. VRRP backup to init  count 

2. VRRP master to init count 

3. VRRP backup to master count 

4. VRRP master to backup count 

5. VRRP init to backup count 

6. VRRP init to master count 
 
This monitored data is then plotted in a time-series chart for analysis purpose.  

### PLATFORM(S) TESTED
8400x

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
