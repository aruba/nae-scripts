## Summary

Monitoring number of ARP requests coming to the switch CPU

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.0: 8400, 9300, 8360, 8325, 8320, 6400, 6300, 6200, 8100, 10000

## Script Description

The main components of the script are monitors, conditions and actions.

This script monitors all ARP related classes in CoPP, setting up NAE Monitors for both traffic passed and dropped and uses periodic callback.

- When the number of ARP requests in the last minute crosses the threshold:
    - The agent will perform some analysis to decide whether it should generate the alert. 
    - Set the Agent Alert Level to Critical
- When the number of ARP requests in the last minute drops below threshold:
    - When the agent detects there is number of ARP requests in the last minute drops below threshold, then it sets the agent alert level back to Normal.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
