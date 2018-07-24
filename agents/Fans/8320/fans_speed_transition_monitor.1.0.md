#### Script File Name: fans\_speed\_transition\_monitor.1.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the speed of all available fans with various supported states like slow, medium, normal, fast and max. This script intends to monitor speed states of fans when there is transition from one speed value to another. 

This script does not intend to probe the actual reason for fans recovery from a high speed state (fast/max) to a Normal (slow/medium/normal) state.  It monitored fans speed states are plotted in time series charts in the WEB-UI and they merely serve as visuals of all the available fans which have moved back to Normal speed , indicating recovery from a previous high speed state

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001

### CONFIGURATION NOTES
The main components of the Hardware Diagnostic "fans_speed_transition_monitor" script are Manifest, Parameter Definitions and the Policy Constructor.   

The 'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined as the intent of the script is to monitor all available fans. The 'Agent Constructor' handles the main logic for monitoring the 'Normal' speed value of all fans. Conditions are defined such that when there is a transition from one speed value to another value and the agent executes a action callback for it. Speed values like slow/medium/normal are considered to be normal speed of a fan and other states like fast/max are considered to be critical speed values of a fan. 

A data structure named 'fans_list' is used to list fans which transited to critical speed state. 

When any fan transit from normal speed values(slow/medium/normal) to any critical speed values(fast/max), then the callback 'fans_speed_action_high' is invoked. The variable 'fans_list' is updated with that fan name and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name. Upon next fan transit to high speed value, the agent displays CLI and syslog with that fan name.  

When the fan at high speed values(fast/max) transit to normal speed values(slow/medium/normal), the fan name in 'fans_list' is removed. When all the fans speed are set back to any normal speed values and 'fans_list' is empty, the agent status is set back to 'Normal'.

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
