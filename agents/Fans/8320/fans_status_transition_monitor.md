#### Script File Name: fan\_status\_transition\_monitor.1.0.py

### SUMMARY
This Hardware Diagnostic Fan script is intended to monitor the status of all available fans with various supported states like empty, uninitialized, ok and fault. This script intends to monitor status of fans when there is transition from one status value to another.

This script does not intend to probe the actual reason for fans recovery from a faulty state to a Normal (ok/uninitialized/empty) state. The monitored fans status are plotted in time series charts in the WEB-UI and they merely serve as visuals of all the available fans which have moved back to Normal state, indicating recovery from a previous  faulty state

### PLATFORM(S) SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "fans_status_transition_monitor" script are Manifest,  Parameter Definitions and the Agent Constructor.   

The 'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined as the intent of the script is to monitor all available Fans.   

The 'Agent Constructor' handles the main logic for monitoring the 'fault' status of all Fans. Conditions are defined such that when there is a transition from one status value to another value, the agent executes a action callback for it. Status values like empty/uninitialized/ok are considered to be normal status of a fan and other states like fault is considered to be critical status value of a fan. A data structure named 'fans_list' is used to list fans which transited to critical status.

When any fan transit from normal status(empty/uninitialized/ok) to critical status(fault), then the callback 'fans_status_action_fault' is invoked.  The variable 'fans_list' is updated with that fan name and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name. Upon next fan transit to fault status, the agent displays CLI and syslog with that fan name.   

When the fan in faulty status(fault) transit to normal status values(empty/uninitialized/ok), the fan name in 'fans_list' is removed.When all the fans status are set back to any normal status values and 'fans_list' is empty, the agent status is set back to 'Normal'.

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
