## Summary

System Power Supply monitoring agent

## Supported Software Versions

Script Version 2.1: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 2.1: 8320, 8325, 8400

## Script Description

The main components of this script are Manifest and the Policy Constructor.   

The  'Manifest' defines the unique name for this script.

The 'Policy Constructor' handles the main logic for monitoring the status and the value of the power supply units.  

The script monitors the transition of the status 
- from ok to fault_input
- from ok to fault_output
- from ok to warning
- from ok to unknown
- from ok to fault_absent
- from fault_output to ok
- from fault_input to ok
- from unknown to ok
- from fault_absent to ok

When there is a transition the agent displays the output from the 'show environment power-supply' command and creates a Syslog message with the transition details. 

The script also monitors and displays the maximum power and the instantaneous power in Watts for all the PSUs. 

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
