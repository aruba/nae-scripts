## Summary

Monitors the route count on the switch

## Supported Software Versions

Script Version 1.1: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 1.1: 6300, 6400, 8320, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code.  
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - Upper Count Threshold: Route count upper threshold value
    - Lower Count Threshold: Route count lower threshold value
The script defines Monitor Resource URI(s), Monitor condition and Action : 
    - Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
        1. Total route count(sum of all URI).

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following:
    - If the total routes count is more than upper count threshold value mentioned in the threshold parameter, the following actions are executed:
        1. The agent alert level is updated to Critical.
        2. A log message is generated with the current routes count on the switch.
    - If the total routes count is less than lower count threshold value mentioned in the threshold parameter, the following actions are executed:
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the routes count is within the threshold value.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
