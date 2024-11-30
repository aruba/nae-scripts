## Summary

This script monitors for broadcast packets storm on an interface and shuts down the interface if the interface shut down option is enabled.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.11 Minimum

## Supported Platforms

Script Version 2.0: 6200, 6300, 64xx

## Summary

The purpose of this script is to help in automatic broadcast storm fault detection which helps protect against network loops. 

## Software Versions Required

Script Version 2.0: ArubaOS-CX 10.11 Minimum

## Platforms Supported

Script Version 2.0: 6200, 6300, 64xx

## Script Description

The main components of the script are monitors, conditions and actions.

- Monitors:  This script monitors the following for all interfaces:
    1. Broadcast storm fault - The user can provide the threshold value for the rate of change of broadcast packets over 20 seconds. For low sensitivity level, the threshold value is 170500, for medium sensitivity level, it is 100000 and for high sensitivity level, it is 29500. 
        - Conditions for this monitor are -
            1. When the threshold provided is for high sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Minor, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at high sensitivity level'.
            2. When the threshold provided is for medium sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Major, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at medium sensitivity level'.
            3. When the threshold provided is for low sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Critical, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at low sensitivity level'.
            4. When there is no longer broadcast storm fault, Syslog says 'Broadcast storm fault detected on interface <name> is back to normal'.
                - If there is no fault found on any of the interfaces, the agent status is marked as Normal.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
