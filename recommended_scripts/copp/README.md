## Summary

This script monitors the CoPP (COntrol Plane Policing) policy configured on the switch. Traffic destined to the switch dropped by CoPP due to a high traffic rate is counted as traffic dropped and traffic allowed to reach the switch control plane will be counted as traffic allowed. Alerts are generated when these rates exceed their respective thresholds. The thresholds are based on the the CoPP Class rates and the values entered by the user as parameters.

## Supported Software Versions

Script Version 5.1: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 5.1: 6200, 6300, 64xx, 8100, 8320, 8325, 8400


## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
