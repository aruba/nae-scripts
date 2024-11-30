## Summary

Client Service Health for Radius, DNS and DHCP

## Supported Software Versions

Script Version 4.2: ArubaOS-CX 10.13.1000 Minimum

## Supported Platforms

Script Version 4.2: 5420, 6200, 6300, 64xx, 8100, 8320, 8325, 8360, 9300, 10000

## Script Description

### Client Services monitor functionality
Clients within the network require a basic set of services in order to
to function on the network. This agent will monitor the following three
services and ensure they are available. The script can be loaded normally
via the WebUI and none of the parameters are required to be configured,
but can be for greater control over thresholds and monitoring.

1. DHCP
The monitoring of DHCP involves the use of ADC lists to ensure the ratio of
server responses and client requests remains near 1:1. If the script
detects the ratio drop below a configurable ratio there will be an alert
fired. This ratio is affected by the number of DHCP servers in the
environment, potentially causing the ratio to drop more slowly with more
servers responding. This agent does not monitor DHCP connectivity when the
switch is acting as the DHCP server or relay nor does it monitor any DHCP
traffic associated with the switch's DHCP client.

Related parameters:
'DHCP_resp_to_req_ratio' - threshold ratio of DHCP responses to requests (Default: '0.7')

2. DNS
Similar to DHCP, DNS will also use ADC lists to monitor the ratio of responses
to requests and fire an alert if it detects the ratio drop below a
configurable ratio. Since DNS uses UDP, but can use TCP when UPD fails or
when the query contains a large response, we will use separate ADC rules to
monitor for either protocol. This agent does not monitor any DNS traffic
associated with the switch's DNS client.

Related parameters:
'DNS_resp_to_req_ratio' - threshold ratio of DNS responses to requests (Default: '0.7')

3. RADIUS
By leveraging the built in RADIUS server tracking feature, we will monitor
the availability of the configured RADIUS servers. The reachablility status
of all of the tracking-enabled servers will be monitored for a change from
'reachable' to 'unreachable' and an alert will be fired if that is detected.

For this agent to be able to monitor radius servers, they each must have tracking enabled via the config CLI.
    ex. (config) radius-server host X.X.X.X tracking enable
The interval for the tracking requests can be configured between 60-86400 seconds (default: 300).
A lower interval may be more desirable for closer monitoring of RADIUS servers.
    ex. (config) radius-server tracking interval 60

Related parameters:
'VRF_name' - used to specify a single VRF to monitor the RADIUS servers on (Default: '*' - will monitor all VRFs)

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
