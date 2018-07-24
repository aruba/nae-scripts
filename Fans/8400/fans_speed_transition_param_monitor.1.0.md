#### Script File Name: fans\_speed\_transition\_param\_monitor.1.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the speed of all available fans with various supported states like slow, medium, normal, fast and max. This script intends to monitor speed states of fans when there is transition from one speed value to another, wherein transition "from" and "to" values are supplied as parameters. The monitored speed value of each fan information be represented in a time-series chart for analysis purpose. 

This script does not intend to probe the actual reason for fans recovery from a high speed state (fast/max) to a Normal (slow/medium/normal) state. The monitored fans speed states are plotted in time series charts in the WEB-UI and they merely serve as visuals of all the available fans which have moved back to Normal speed , indicating recovery from a previous high speed state

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001

### CONFIGURATION NOTES
The main components of the Hardware Diagnostic "fans_speed_transition_param_monitor" script are Manifest, Parameter Definitions and the Agent Constructor.   

The 'Manifest' defines the unique name for this script. The 'Parameter Definitions' has parameters like "transition_from" and "transition_to" which is supplied in the transition condition for "from" and "to" respectively. The parameters values can be slow/medium/normal/fast/max. The default value for "transition_from" and "transition_to" are "normal" and "max" respectively. 

The 'Agent Constructor' handles the main logic for monitoring the transition from one speed value to another speed value as supplied by the user in as parameters. User can monitor the transition of each fan from one state to another of there interest as supplied by the user in the parameters.  

When the transition condition is met, action "fan_speed_transition_action" is invoked. This action displays CLI output for 'show environment fan', as well as syslog which displays the fan name which took transition from one speed value to another as expected by the user. 

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
