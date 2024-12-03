## Summary

Monitor rate of decrease of neighbors

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.0: 6200, 6300, 64xx, 8320, 8325, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    1. rate_of_decrease_threshold -  Rate of decrease threshold (in percentage)
    2. time_interval - Time interval for calculating rate of decrease

The script defines Monitor Resource URI(s), Monitor condition and Action : 
- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Sum of Count of the Neighbors across all VRFs.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following:
    - A periodic callback executed every interval of time as expected as time_interval NAE parameter.
    - The periodic callbacks makes a REST call to obtain the sum of count of all Neighbors across all VRFs.
    - Using the obtained value, calculate the rate of decrease by subtracting it from the previous value and dividing it by the time interval.
    - If the decrease rate is more than threshold value mentioned in the rate_of_decrease_threshold parameter, the following actions are executed:
        1. The agent alert level is updated to Critical.
        2. A log message is generated with the rate of decrease value
        3. A custom report is generated with the rate of decrease value
    - When the rate of decrease is less than the threshold value, the following actions are executed:
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the rate of decrease value
        3. A custom report is generated with the rate of decrease value

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
