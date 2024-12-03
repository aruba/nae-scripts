## Summary

This script monitors the reachability between two devices given the IP-SLA session.The IP-SLA session has to be configured in the switch before using this script to monitor the connectivity/reachability between two devices.

## Supported Software Versions

Script Version 3.0: ArubaOS-CX 10.11 Minimum

## Supported Platforms

Script Version 3.0: 8320, 8325

## Script Description

The main components of the script are Manifest, Parameter Definitions and the python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters:
    1. connectivity_check_rate – the rate at which, status of the connectivity is checked. The value should be (at the least) twice the probe-interval of the IP-SLA session. It is measured in minutes. Default value is 1 minute (assuming the min probe-interval as 5 seconds.)
    2. ipsla_session_name - This parameter specifies ipsla-session name. Default value is ' '.

The script defines Monitor(s), Condition(s) and Action(s):

- Monitors: 
    1. Last Probe Time - (A placeholder monitor for the periodic call-back). Monitors the last_probe_time of the ip-sla session. This does not help in generating any alerts or action call-back. 
    2. State - (Only for Graph display). Monitor the state( state of IPSLA Session). Shows DNS Failure, Config failure etc...This monitor is used only for plotting the graph, does not help in generating any alerts.  But this field in graph does justify and reason the alerts created. 
    3. Probes Timed Out - (Only for Graph display). Monitor the probes timed out of IPSLA session.  if the connection is lost, the value of probes-timed-out is incremented, indicating the connection lost.  
    This monitor is used only for plotting the graph and does not help in generating any alerts. But this field in graph does justify and reason the alerts created. 
- Conditions: 
    1. Periodic call back for every connectivity_check_rate in minutes.
- Actions:
    1. Minor alert - When the connectivity between the source and destination is lost for the specific probe, minor alert is created.
    2. Critical alert – If the connectivity is still lost after the Minor alert, to indicate the consistent loss of connectivity a critical alert is generated.
    3. Normal alert -  When the connectivity between the source and destination IP is restored, Normal alert is generated.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
