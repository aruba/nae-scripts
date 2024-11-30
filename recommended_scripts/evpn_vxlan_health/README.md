## Summary

Agent for monitoring EVPN and VxLAN health

## Supported Software Versions

Script Version 3.0: ArubaOS-CX 10.13.1000 Minimum

## Supported Platforms

Script Version 3.0: 6200, 6300, 64xx, 8325, 8360, 8400, 10000, 8100

## Script Description

The overall, terse goal of this script is to monitor evpn and vxlan health, decide if things have gone bad, and if so, generate some helpful cli/shell output from the appropiate moment of the event.

Agents derived from this script will monitor three areas: 

1. EVPN
    - monitor EVPN Instances
    - alert if
        - EVPN instance state changed from operational to non-operational
        - EVPN instance stuck in non-operational state for 5 cycles
        - EVPN instance is deleted
        - Peer VTEP deletion for a EVPN instance
        - No. of VTEP Peers, Local MACs, Remote MACs, Remote Routes learnt on an EVPN instance decreases greater than 20% between 2 cycles
    - publish output from:
        - show evpn evi summary - lists EVPN instances and state (up/down)
        - show evpn evi <evpn_instance> detail - detail info about single EVPN instance. state, peer-vtep, rd/rt, statistics
        - show evpn mac-ip evi <evpn_instance> - lists remote MACs / Routes learnt by evpn instance
        - show interface vxlan 1 brief - to know if interface vxlan 1 is down
        - show interface vxlan 1 - information about interface vxlan 1 state and list of VTEPs
        - show interface vxlan vteps <tunnel_endpoint_ip> - to check state of particular tunnel endpoint
        - show interface vxlan vteps - to check which tunnels are remaining when more than 20% tunnels are deleted. Lists tunnels, VNI and tunnel state
        - show bgp l2vpn evpn summary - list bgp l2vpn neighbors and their state
        - show ip route <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check if route is present for tunnel_endpoint_ip
        - ping <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check ping connectivity to tunnel endpoint
        - traceroute <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check connectivity to nexthop and tunnel endpoint
        - show mac-address-table | inc evpn | count - to check count of remote MACs learnt
        - show mac-address-table | inc dynamic | count - to check count of local MACs learnt
        - syslogs to indicate the evi deletion, peer vtep deletion, evi state change, operational failure reason, percentage decrease of the MAC/Peer VTEP counts
    - clear alert if
        - All EVPN Instances in JSON response are in operational state
    - filters
        - based on EVPN instance, tunnel endpoint destination IP, VRF of tunnel endpoint
    - alerts
        - MAJOR
            - EVPN instance stuck in non-operational state for 5 cycles
        - MINOR
            - EVPN instance is deleted
            - EVPN instance state changed from operational to non-operational
            - Peer VTEP is deleted for a EVPN instance
            - No. of Vtep Peers, Local MACs, Remote MACs, Remote Routes learnt on a EVPN instance decreases greater than 20% between 2 cycles

2. Tunnel Endpoint
    - monitor Tunnel Endpoint
    - alert if
        - Tunnel Endpoint state changed from operational to non-operational
        - Tunnel Endpoint stuck in non-operational state for 5 cycles
    - publish output from:
        - show interface vxlan vteps <tunnel_endpoint_ip> <tunnel_endpoint_vrf> - to check state of particular tunnel endpoint
        - show bgp l2vpn evpn summary - list bgp l2vpn neighbors and their state
        - show ip route <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check if route is present for tunnel_endpoint_ip
        - ping <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check ping connectivity to tunnel endpoint
        - traceroute <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check connectivity to nexthop and tunnel endpoint
    - clear alert if
        - All tunnels in JSON response are in operational state
    - filters
        - based on tunnel endpoint destination IP and VRF of tunnel endpoint
    - alerts
        - MAJOR
            - Tunnel Endpoint state changed from operational to non-operational
        - MINOR
            - Tunnel Endpoint stuck in non-operational state for 5 cycles

3. VNI health
    - monitor virtual network id health
    - alert if
        - VNI state/forwarding state stuck in non-operational state
        - VNI state/forwarding state going down from stable operational state
        - VNI config state stuck in invalid
    - publish output from:
        - show interface vxlan vni <VNI_ID>
        - show running-config interface vxlan 1
    - clear alert if moving back to operational from non-operational state
    - filters
        - based on VNI_ID
    - alerts
        - Major
            - VNI state/forwarding state going down from stable operational state
            - VNI config state stuck in invalid
        - Minor
            - VNI state/forwarding state stuck in non-operational state

Note:
- The Maximum of alert conditions processed in one poll cycle is a configurable parameter. With a minimum of 1, maximum of 6 and default of 3 alerts in one poll cycle.
- If the system goes down to bad state and comes back to good state within the polling interval, the event will be missed and alert will not happen

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
