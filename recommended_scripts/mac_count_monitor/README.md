## Summary

Agent to monitor count of MAC address learnt 

## Supported Software Versions

Script Version 2.1: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 2.1: 6300, 6400, 8320, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code. 
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - Threshold -  Total MAC address count threshold

The script defines Monitor Resource URI(s), Monitor condition and Action : 
- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Total MAC addresses count(sum of all URI).

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following: 
    - If the total Mac addresses count is more than threshold value mentioned in the threshold parameter, the following actions are executed:
        1. A log message is generated with the total MAC addresses on the switch .
        2. The agent alert level is updated to Critical.
    - When the rate of total Mac addresses count is less than the threshold value, the following actions are executed. 
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the rate of decrease value.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
