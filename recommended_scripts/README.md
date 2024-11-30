# Recommended NAE Scripts

These are the scripts recommended by HPE Aruba Networks for customers to use on their switches. These scripts have been tested and determined to add value.  Below is a list of all of the scripts with a short description. You can click on each script directory to see all available versions (different versions have different firwmare support), as well as a README with a more detailed description of each script.  All of these scripts can also be seen in the switch Web UI NAE script portal.

### copp:
This script monitors the CoPP (COntrol Plane Policing) policy configured on the switch. Traffic destined to the switch dropped by CoPP due to a high traffic rate is counted as traffic dropped and traffic allowed to reach the switch control plane will be counted as traffic allowed. Alerts are generated when these rates exceed their respective thresholds. The thresholds are based on the the CoPP Class rates and the values entered by the user as parameters.

### lag_health_monitor:
LAG status monitoring agent using PSPO

### mac_count_monitor:
Agent to monitor count of MAC address learnt 

### daemon_resource_monitor:
Top 4 System daemon CPU & Memory utilization monitoring agent

### routes_decrease_rate_monitor:
Monitor rate of decrease of routes

### connectivity_monitor:
This script monitors the reachability between two devices given the IP-SLA session.The IP-SLA session has to be configured in the switch before using this script to monitor the connectivity/reachability between two devices.

### power_supply_monitors:
System Power Supply monitoring agent

### configuration_change_tftp:
Agent to copy the running configuration to a TFTP server whenever a configuration change occurs.

### broadcast_storm_monitor:
This script monitors for broadcast packets storm on an interface and shuts down the interface if the interface shut down option is enabled.

### routing_health_monitor:
Agent for monitoring routing health

### arp_request_monitor:
Monitoring number of ARP requests coming to the switch CPU

### configuration_change_topdesk:
Agent to alert user when configuration changes and show the system info and diff of configuration changes. An incident is created in TOPdesk, with the diff of configuration changes and other details.

### neighbors_count_monitor:
Agent to monitor number of neighbors learnt using ARP

### configuration_change_service_now:
Agent to alert user when configuration changes and show the system info and diff of configuration changes. A ticket is created in Incident table of ServiceNow, with the diff of configuration changes and other details.

### vsf_health_monitor:
This script monitors the role, status, cpu and memory usage, stack_split_state and topology type of VSF Stack

### vsx_health_monitor:
VSX Health monitoring

### software_device_health_monitor:
This script monitors overall software device health.

### evpn_vxlan_health:
Agent for monitoring EVPN and VxLAN health

### ipsla:
Monitor particular value/aggregate value of an SLA test and specify shell command to run as action

### configuration_change_email:
Agent to alert user when configuration changes and show the system info and diff of configuration changes. An email notification with the diff is sent whenever the configuration changes.

### client_services_health:
Client Service Health for Radius, DNS and DHCP

### hardware_device_health_monitor:
This script monitors the overall hardware device health.

### route_count_monitor:
Monitors the route count on the switch

### fans_speed_transition_monitor:
Agent to monitor speed of all fans, wherein the transition between different speed states is monitored. The agent status is set to Critical when any of the fan speed has transition from normal/medium/slow to max/fast. The status remains in Critical, when other fans speed transits to max/fast, and syslog and cli are displayed.The agent status is set back to normal when all the fans are in normal/medium/slow state.

### neighbors_decrease_rate_monitor:
Monitor rate of decrease of neighbors

### application_health_monitor:
Network Analytics agent script to monitor application health

