## Summary

Monitoring number of ARP requests coming to the switch CPU

## Supported Software Versions


## Supported Platforms


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
