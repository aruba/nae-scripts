#### Script File Name: fans\_monitor.2.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the status, speed and rpm value of a specified fan. The supported states for speed are slow, medium, normal, fast and max. Supported states for status are empty, uninitialized, ok and fault.  

 This script does not intend to probe the actual reason for fan's failure or increase in its speed (caused due to fan status transitioning to fault state or fan rpm value exceeding a tolerable level). The monitored fan rpm value/status/speed transition states serve as quick visuals indicating the underlying fault/warning of the specified fan only

### PLATFORM(S) SUPPORTED
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "fan_monitor" script are Manifest, ParameterDefinitions and the Agent Constructor.    

The  'Manifest' defines the unique name for this script and 'ParameterDefinitions' has one parameter named 'fan_name' to indicate the fan name of which the speed, status and rpm values to be monitored. The default value for the parameter 'fan_name' in case of 8400 switch is 1/1/1 , which belongs to fan_tray 1/1 .  

The 'Agent Constructor' handles the main logic for monitoring the speed, status and rpm value of the specified Fan. The first Monitor Resource URI defined is to monitor the status transition of the specified fan. This monitored data is plotted in a time-series chart for analysis purpose. The agent status will be set to 'critical' when the fan status value transited to 'fault'.

The second Monitor Resource URI defined is to monitor the speed transition of the specified fan. This monitored data is plotted in a time-series chart for analysis purpose. The agent status will be set to 'major' when fan speed value transited to 'fast' and 'critical' when the fan speed value transited to 'max'.

The third Monitor Resource URI defined monitors the rpm value of the Fan and no Action is taken corresponding to this. The monitored rpm value over time is  plotted in a time-series chart for analysis purpose.

When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command ('show environment fan') is displayed in Alert Window and the agent status is changed as per transition state severity.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
