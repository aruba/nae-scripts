## Summary

Network Analytics agent script to monitor application health

## Supported Software Versions

Script Version 2.2: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.2: 5420, 6300, 64xx, 8100, 8320, 8325, 8400, 8360, 9300, 10000

## Configuration Notes

The main components of the script are Manifest, Parameter Definitions and python code. 

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - TCP_Application_IP_Address: Server to monitor for anomalies
    - TCP_Application_Port: TCP protocol port for the application
    - TCP_Application_VRF: VRF for the application
    - TCP_SYN_Ratio: Minimum ratio of server SYN/ACK to client SYN packets
    - VoIP_IPSLA_Name: VOIP IP-SLA session to monitor for anomalies
    - VoIP_Min_MOS: Minimum MOS service level
    - HTTP_IPSLA_Name: HTTP IP-SLA session to monitor for anomalies
    - HTTP_Max_RTT: Maximum RTT service level
- Monitors:  This script specifies the monitoring URI(s) to monitor the following: 
    - Connection request rate (packets per second)
    - Connection response rate (packets per second)
    - Connection reset rate (packets per second)
    - Client to server traffic (packets per second)
    - Server to client traffic (packets per second)
    - TCP Connection ADC Status
    - IPSLA State Monitor
    - IPSLA Type Monitor
    - IPSLA Session Statistics
        - bind_error
        - destination_address_unreachable_count
        - dns_resolution_failures
        - probes_timed_out
        - socket_receive_error
        - transmission_error
- Actions:  This script performs the following actions:
    - When SYN/ACK to SYN ratio changes, it changes agent level to critical & executes CLI command.
    - When this ratio gets to normal, agent status sets to normal. Along with this agent report generated & previous critical alert gets deleted.
    - When ADC status changes, Agent status is set to Minor & agent report generated.
    - When this status gets back to normal, previous alert gets deleted & agent report generated.
    - When VOIP packets rx error detected, agent status is set to minor & agent report generated.
    - When this error clears, corresponding alert is deleted & html report is generated.
    - When IPSLA state is not running, agent status is set to minor & agent report generated.
    - When IPSLA state is  running, corresponding alert is deleted & html report is generated.
    - When IPSLA type error detected, agent status is set to minor & agent report generated.
    - When IPSLA type error cleared, corresponding alert is deleted & html report is generated.
    - When IPSLA value anomaly detected, agent status is set to critical & agent report generated.
    - When IPSLA value anomaly cleared, corresponding alert is deleted & html report is generated.
    - When IPSLA session statistics have a count greater than 0, agent status is set to minor & agent report generated.
    - When IPSLA session statistics have a count equal to 0, corresponding alert is cleared & html report is generated.

## Script Limitations

The path of traffic within VSX topologies may raise false positive alerts; specifically, when traffic is received by VSX#1 and transmitted by VSX#2.
For instance, suppose there exists a two-member VSX topology with devices VSX#1 and VSX#2. Both devices have the Application Health script configured and agents deployed.  The client (application) sends requests to a server, so the traffic goes from Client -> L2 Switch -> VSX#2 -> VSX#1 -> Server. When the server responds, the traffic goes from Server -> VSX#1 -> L2 Switch -> Client (skipping VSX#2), and generates a false critical alert in VSX#2.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
