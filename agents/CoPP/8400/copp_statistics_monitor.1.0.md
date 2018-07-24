#### Script File Name: copp\_statistics\_monitor.1.0.py

### SUMMARY
This Control Plane Policing (CoPP) statistics monitoring script is intended to monitor CoPP statistics (number of packets dropped or passed) for given CoPP class.

Switch CLI command 'show copp-policy statistics' can be executed to know about the supported CoPP classes. Examples for CoPP class are  stp, default, vrrp, sflow, dhcp, bgp-ipv4, icmp-broadcast-ipv4 etc.

Default CoPP class is in the script ‘total’ which monitors the total number of packets passed or dropped    

### PLATFORMS SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

### SCRIPT DESCRIPTION
The main sections of the CoPP statistics script are Manifest, ParameterDefinitions and the Agent Constructor.     

The ’Manifest’ section defines the unique name for this script with short description about script purpose.  

'ParameterDefinitions' section defines script parameters, in this case CoPP class name to monitor.

The 'Agent Constructor' handles the main logic for monitoring CoPP statistics for the given CoPP class. Statistics (Number of packets passed and dropped) for the given CoPP class will be presented as a time series graph for analysis purpose.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
