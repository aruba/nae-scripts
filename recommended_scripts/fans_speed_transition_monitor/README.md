## Summary

Agent to monitor speed of all fans, wherein the transition between different speed states is monitored. The agent status is set to Critical when any of the fan speed has transition from normal/medium/slow to max/fast. The status remains in Critical, when other fans speed transits to max/fast, and syslog and cli are displayed.The agent status is set back to normal when all the fans are in normal/medium/slow state.

## Supported Software Versions

Script Version 1.0: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 1.0: 8320, 8400

## Script Description

The main components of the Hardware Diagnostic "fans_speed_transition_monitor" script are Manifest, Parameter Definitions and the Policy Constructor.   

The 'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined as the intent of the script is to monitor all available fans. The 'Agent Constructor' handles the main logic for monitoring the 'Normal' speed value of all fans. Conditions are defined such that when there is a transition from one speed value to another value and the agent executes a action callback for it. Speed values like slow/medium/normal are considered to be normal speed of a fan and other states like fast/max are considered to be critical speed values of a fan. 

A data structure named 'fans_list' is used to list fans which transited to critical speed state. 

When any fan transit from normal speed values(slow/medium/normal) to any critical speed values(fast/max), then the callback 'fans_speed_action_high' is invoked. The variable 'fans_list' is updated with that fan name and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name. Upon next fan transit to high speed value, the agent displays CLI and syslog with that fan name.  

When the fan at high speed values(fast/max) transit to normal speed values(slow/medium/normal), the fan name in 'fans_list' is removed. When all the fans speed are set back to any normal speed values and 'fans_list' is empty, the agent status is set back to 'Normal'.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
