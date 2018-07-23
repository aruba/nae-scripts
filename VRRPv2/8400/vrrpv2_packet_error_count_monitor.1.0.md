#### Script File Name: vrrpv2\_packet\_error\_count\_monitor.1.0.py

### SUMMARY
This script monitors VRRPv2 statistics related to invalid, error or mismatch packet count for the specified VRRP Id and interface in the system. The interface name can be a physical, vlan or lag interface

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001


### CONFIGURATION NOTES

The main components of the script are Manifest, Parameter Definitions and the Policy Constructor.   

'Manifest' defines the unique name for this script. This script uses the following name:  vrrpv2_packet_error_count_monitor 

'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 

vrrp_id – This parameter specifies VRRPv2 instance unique id. Default value is 1 

port_name - This parameter specifies the interface that this agent will monitor for any VRRP state   changes. This can be a physical, vlan or lag interface. Default value is 1/1/1 

advertise_interval_errors – This parameter specifies the number of times VRRPv2 Advertisement packets are sent at an incorrect interval. Default value is 1, monitoring can be turned off by specifying value 0 

advertise_recv_in_init_state - This parameter specifies the number of times VRRPv2 Advertisement packets are received in init state. Default value is 0, monitoring can be turned on by specifying value 1 

advertise_recv_with_invalid_len - This parameter specifies the number of VRRPv2packets with invalid length. Default value is 0, monitoring can be turned on by specifying value 1 

advertise_recv_with_invalid_ttl - This parameter specifies the number of VRRPv2 packets with TTL errors. Default value is 0, monitoring can be turned on by specifying value 1 

advertise_recv_with_invalid_type -  This parameter specifies the number of received VRRPv2 packets of invalid type. Default value is 0, monitoring can be turned on by specifying value 1 

ip_address_owner_conflicts - This parameter specifies the number of VRRPv2 packets with  ip address owner conflicts. Default value is 0, monitoring can be turned on by specifying value 1 

mismatched_addr_list_pkts - This parameter specifies the number of VRRPv2 packets with incorrect virtual IP address lists. Default value is 0, monitoring can be turned on by specifying value 1 

mismatched_auth_type_pkts - This parameter specifies the number of VRRPv2 packets with a non-matched authentication mode.. Default value is 0, monitoring can be turned on by specifying value 1 

near_failovers - This parameter specifies the Number of Near Failovers statistic. Default value is 0, monitoring can be turned on by specifying value 1 

other_reasons - This parameter specifies the Number of other errors statistics. Default value is 0, monitoring can be turned on by specifying value 1 

 

#### 'Policy Constructor' defines Monitor Resource URI. This script specifies  monitoring uri's to monitor the following:  

1. VRRPv2 Advertisement packets are sent at an incorrect interval count 

2. VRRPv2 Advertisement packets are received in init state count 

3. VRRPv2packets with invalid length count 

4. VRRPv2 packets with TTL errors count 

5. VRRPv2 packets of invalid type count 

6. VRRPv2 packets with  ip address owner conflicts count 

7. VRRPv2 packets with incorrect virtual IP address lists count 

8. VRRPv2 packets with a non-matched authentication mode count 

9. VRRPv2 Near Failovers statistics count 

10. VRRPv2 errors statistics count 

This monitored data is then plotted in a time-series chart for analysis purpose.  

### PLATFORM(S) TESTED
8400x

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
