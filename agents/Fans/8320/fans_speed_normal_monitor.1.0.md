#### Script File Name: fans\_speed\_normal\_monitor.1.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the speed of all available fans with various supported states like slow, medium, normal, fast and max and the monitored speed value of each fan information be represented  in a time-series chart for analysis purpose.

 This script does not intend to probe the actual reason for fans recovery from a high speed state (fast/max) to a Normal (slow/medium/normal) state. The monitored fans speed states are plotted in time series charts in the WEB-UI and they merely serve as visuals of all the available fans which have moved back to Normal speed , indicating recovery from a previous high speed state

### PLATFORM(S) SUPPORTED
 8400X
 8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "fans_speed_normal_monitor" script are Manifest,  ParameterDefinitions and the Agent Constructor.   

 The  'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined as the intent of the script is to monitor all available Fans.  

 The 'Agent Constructor' handles the main logic for monitoring the 'Normal' speed value of all Fans. Conditions are defined such that each speed state is monitored. States like slow/medium/normal are considered to be normal speed of a fan and other states like fast/max are considered to be critical speed values of a fan. A data structure named 'fans_list' is used to list fans which transited to critical speed state and 'speedy_fans_count' is used to count the number of fans which are at high speed.    

When any fan transit to any critical speed value, then the callback 'fans_speed_action_high' is invoked.  The variable 'fans_list' is updated with that fan name and 'speedy_fans_count' is incremented and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name and number of fans at high speed. Upon next fan transit to high speed value, the agent displays CLI and number of fans at high speed.  

 When the fan at high speed transit to normal speed (slow/medium/normal), the fan name in 'fans_list' is removed and 'speedy_fans_count' is decremented. When all the fans speed are set back to any normal speed value and 'fans_list' is empty, the agent status is set back to 'Normal'.

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
