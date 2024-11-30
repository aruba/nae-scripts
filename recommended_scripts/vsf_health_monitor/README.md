## Summary

This script monitors the role, status, cpu and memory usage, stack_split_state and topology type of VSF Stack

## Supported Software Versions

Script Version 3.0: ArubaOS-CX 10.13.1000 Minimum

## Supported Platforms

Script Version 3.0: 6200, 6300

## Script Description

The overall goal of this script is to monitor vsf events and generate some helpful cli/shell output from the appropriate moment of the event.

Agents derived from this script will monitor these areas:

1. VSF Status
    - monitor status changes
    - alert if
        - VSF status changes to unassigned, version_mismatch, not_present, booting, stack_split and ready
        - show vsf - shows the information of the stack with mac address
2. VSF Role
    - monitor role changes
    - alert if
        - VSF role changes to standby, member, unassigned.
        - show vsf - shows the information of the stack with mac address
3. CPU and Memory usage
    - monitor cpu and memory utilization monitoring
    - alert if
        - CPU and Memory utilization exceeds the threshold value
        - top cpu - will give the information of the cpu utilization
        - top memory - memory utilization
4. VSF Topology
    - monitor topology type
    - alert if
        - Topology changes from ring to chain        - Topology change to standalone in case of stack_split
        - show vsf - show the information of the stack with mac address
        - show vsf topology - shows the topology diagram of the stack
5. VSF Stack split status
    - monitor stack_split_status change
    - alert if
        - stack_split_state is active_fragment,inactive_fragment or no_split
        - show vsf - shows the information of the stack with mac address and stack_split_state

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
