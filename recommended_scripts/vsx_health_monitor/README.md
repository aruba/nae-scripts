## Summary

VSX Health monitoring

## Supported Software Versions

Script Version 4.0: ArubaOS-CX 10.13.1000 Minimum

## Supported Platforms

Script Version 4.0: 64xx, 8100, 8320, 8325, 8360, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    1. routes_count_ratio_lower_threshold -  Route count deviation lower threshold
    2. routes_count_ratio_upper_threshold - Route count deviation upper threshold
    3. neighbors_count_ratio_lower_threshold - Neighbors count deviation upper threshold
    4. neighbors_count_ratio_upper_threshold - Neighbors count deviation lower threshold
    5. mac_addresses_count_ratio_lower_threshold - MAC addresses count deviation lower threshold
    6. mac_addresses_count_ratio_upper_threshold - MAC addresses count deviation upper threshold

The script defines Monitor Resource URI(s), Monitor condition and Action:

- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Sum of count of the Routes across all VRFs on both the switch and the VSX-peer switch.
    2. Sum of count of the Neighbors across all VRFs on both the switch and the VSX-peer switch.
    3. Sum of count of MAC addresses across all VLANs on both the switch and the VSX-peer switch.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script performs the following actions:
    - Whenever the ratio of the sum of count of Neighbors or MAC_Addresses on the switch to the VSX-peer switch is out of the range bounded by the upper threshold and lower threshold for resource, the agent alert level is set to Critical.
    - Whenever the ratio of the sum of count of Routes on the switch to the VSX-peer switch is out of the range bounded up the upper and lower threshold values for routes, the agent alert level is set to Minor if the current alert level is Normal. If the current alert level is Critical , the agent alert level remains critical.
        - A log message and custom report are generated giving the count of the resource on the switch
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning that the ratio is outside the range bounded by the thresholds for that resource.
    - When the ratios for all the three resources (Neighbors, Routes  and MAC Addresses) are within the range specified by the threshold for the resource, the agent alert level is set to nornal with the following actions:
        - A log message and custom report are generated giving the count of the resource on the switch
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning is inside the range bounded by the thresholds for that resource.
    - When the ratios for Neighbors and MAC Addresses are within the range specified by the threshold for the resource but the ratio of Routes is outside the range specified by the threshold for Routes, the agent alert level is set to Minor with the following actions:
        - A log message and custom report are generated giving the count of the resource on the switch.
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning is inside the range bounded by the thresholds for that resource.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
