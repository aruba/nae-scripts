## Summary

This script monitors the CoPP (COntrol Plane Policing) policy configured on the switch. Traffic destined to the switch dropped by CoPP due to a high traffic rate is counted as traffic dropped and traffic allowed to reach the switch control plane will be counted as traffic allowed. Alerts are generated when these rates exceed their respective thresholds. The thresholds are based on the the CoPP Class rates and the values entered by the user as parameters.

## Supported Software Versions

Script Version 5.1: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 5.1: 6200, 6300, 64xx, 8100, 8320, 8325, 8400

## Configuration Notes

An agent can be created for the script on the device. The following parameters can be set while creating agent:

- Monitoring Profile - Determines the monitoring profile to load
        - ALL - Monitors dropped and allowed traffic for each CoPP class in the applied policy
        - DROPS - Monitors dropped traffic for each CoPP class in the applied policy
        - RECOMMENDED - Monitors dropped traffic for DHCP, ARP Broadcast, IP Exceptions, Unknown Multicast, Unresolved IP Unicast, and Total dropped/allowed traffic
- Dropped Traffic Alert Threshold - Alert will fire when rate of dropped traffic exceeds this threshold
- Allowed Traffic Alert Threshold - Alert will fire when rate of allowed traffic exceeds this threshold

## Script Description

The main components of this script are monitors, conditions and actions.

The script monitors the traffic passed or dropped for certain CoPP classes based on the monitoring profile. 

For each monitored CoPP class -

- When the traffic dropped is greater than the threshold:
    - The agent will perform some analysis to decide whether it should generate the alert or not. The decision of alerting is made based on the history of packet drops of all CoPP classes, ignoring the acl_logging, sflow and total classes.  
    After fetching the history, if at least one class had an increase in the traffic dropped, then the agent takes two actions:

        - Set the Agent Alert Level to Critical
        - Build an Analysis Report with the following information of each class:
            1. Traffic passed 
            2. Traffic dropped 
            3. % of contribution to the total of traffic passed
            4. % of contribution to the total of traffic dropped
            5. Priority, Burst and Rate configured for the Class  
            The columns of this report can be sorted. This can be used to facilitate the identification of the top-most offending classes, simply by sorting the column for traffic dropped over the last 15 seconds.
- When the traffic dropped is less than the threshold:
    - When the agent detects there is no CoPP class dropping traffic anymore, then it sets the agent alert level back to Normal.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
