## Summary

Agent to monitor speed of all fans, wherein the transition between different speed states is monitored. The agent status is set to Critical when any of the fan speed has transition from normal/medium/slow to max/fast. The status remains in Critical, when other fans speed transits to max/fast, and syslog and cli are displayed.The agent status is set back to normal when all the fans are in normal/medium/slow state.

## Supported Software Versions

Script Version 1.0: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 1.0: 8320, 8400


## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
