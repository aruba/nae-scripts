## Summary

Top 4 System daemon CPU & Memory utilization monitoring agent

## Supported Software Versions

Script Version 4.2: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 4.2: 6200, 6300, 64xx, 8320, 8325, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code. 

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - cpu_threshold -  High CPU threshold value in percentage
    - memory_threshold: High Memory threshold value in percentage
    - time_interval: Time interval in seconds to consider CPU/Memory utilization
    - daemon_1: ops-switchd
    - daemon_2: ovsdb-server
    - daemon_3: hpe-routing
    - daemon_4: ndmd

The script defines Monitor Resource URI(s), Monitor condition and Action : 
- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. CPU (CPU/Memory utilization in %)
    2. Memory (CPU/Memory utilization in %)

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following: 
    - If the CPU/Memory utilization is more than threshold value mentioned in the threshold parameter for a specific time interval, the following actions are executed:
        1. A log message is generated with the high CPU/Memory utilization by daemon.
        2. The agent alert level is updated to Critical.
    - When the CPU/Memory utilization is less than the threshold value for a specific time interval, the following actions are executed. 
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the CPU/Memory utilization back to normal for daemon.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
