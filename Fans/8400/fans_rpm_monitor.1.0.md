#### Script File Name: fans\_rpm\_monitor.1.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the rpm values of all available fans in the system. 

This script does not intend to probe the actual reason for fans high or low rpm values. 

It monitors the fans rpm values and are plotted in time series chart. In the WEB-UI and they merely serve as visuals of all the available fans

### MINIMUM SOFTWARE VERSION REQUIRED 
ArubaOS-CX XL/TL.10.01.0001

### CONFIGURATION NOTES
The main components of the Hardware Diagnostic "fans_rpm_monitor" script are Manifest, Parameter Definitions and the Agent Constructor.   

The  'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined. The 'AgentConstructor' defines an URI to capture the rpm values of all fans. The monitored data is then plotted in a time-series chart for analysis purpose.

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
