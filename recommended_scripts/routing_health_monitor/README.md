## Summary

Agent for monitoring routing health

## Supported Software Versions

Script Version 3.1: ArubaOS-CX 10.13.1000 Minimum

## Supported Platforms

Script Version 3.1: 5420, 6200, 6300, 64xx, 8100, 8320, 8325, 8360, 8400, 9300, 10000

## Script Description

The overall, terse goal of this script is to monitor routing health, decide if things have gone bad, and if so, generate some helpful cli/shell output from the appropiate moment of the event.

Agents derived from this script will monitor three areas:
1. COPP
    - monitor COPP stat: "unresolved_ip_unicast_packets_dropped"
    - alert if 1, 5, or 10 minute moving average increases above 10 percent of the system capacity
    - publish output from:
        - show copp statistics non-zero
        - show ip route summary all-vrfs
        - ovsdb incomplete routes
        - ovsdb  incomplete neighbors
        - l3 resource manager capacities
    - clear alert if moving averages drop below 1 percent of system capacity
2. OSPF
    - monitor OSPF neighbors
    - alert if
    - OSPF neighbors getting expired
    - OSPF neighbors getting stuck in ex_start, exchange, init states
        - alert is set between ospf threshold time and upto 5 poll cycles
    - OSPF neighbors going down from stable full and two_way adjacencies
    - OSPF neighbors going down from LSA exchange process
    - publish output from:
    - show interface stats - to know the ospf tx/rx statistics and errors
    - debug ospf port - debug one of the ospf interfaces which alerted
        - enable only in one else too much data to debug
        - collects data for 5 poll cycles
        - display at the end of 5 poll cycles
    - ping to the neighbor few times
    - clear alert if
    - All neighbors present are in good state
    - filters
    - based on vrf, area or interface ( interface-list can be given separated by comma )
    - alerts
        - CRITICAL
            - neighbor stuck in states ex_start/exchange/init
        - MAJOR
            - neighbor state change from full to init/down/exchange/ex_start
            - neighbor state change from two_way to init/down
            - neighbor state change from exchange to init/down/two_way/ex_start
            - neighbor state change from ex_start to init/two_way/down
        - MINOR
            - neighbor expired
3. BGP
    - monitor BGP neighbors
    - alert if
    - BGP neighbors getting stuck in Idle, Active, Connect, OpenConfirm states
        - alert is set between BGP threshold time and upto 5 poll cycles
    - BGP neighbors going down from Established state
    - BGP neighbor state flaps within a single poll interval
    - BGP neighbor exchanges a new error, sub-error code than before
    - BGP neighbor added or deleted
    - publish output from:
    - show bgp all summary - to know all the neighbor states
    - ping <bgp_nbr> <source> - to check if peer address is reachable
    - traceroute <bgp_nbr> - to check where is the packet dropped
    - syslogs to indicate the error and sub-error codes sent/received from BGP neighbor
    - clear alert if
        - All neighbors present are in good state
    - filters
    - based on vrf, neighbor address
    - alerts
        - CRITICAL
            - neighbor state changed from estabished to idle/connect/active/OpenConfirm
        - MAJOR
            - neighbor is flapping( neighbor state is 'established' in last and
            current cycle but 'bgp_peer_established_count' in current cycle is greater
            than last cycle)
        - MINOR
            - neighbor stuck in states idle/connect/active/OpenConfirm
            - neighbor deleted
4. Routing health
    - monitor Routing daemon high cpu
    - alert if
        - CPU stays high for cpu_threshold for cpu_time_interval
    - actions
        - for the cpu_cooldown_interval do not query ospf/bgp neighbors
        - do not case additional cpu spike
        - give time for cool down

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
