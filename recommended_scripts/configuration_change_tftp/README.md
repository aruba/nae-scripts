## Summary

Agent to copy the running configuration to a TFTP server whenever a configuration change occurs.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.0: 8320, 8325, 8400

## Script Description

- Parameter Definitions' defines the input parameters to the script.  
This script requires the following parameters:
        1. tftp_server_address - IP address of the TFTP server.
        2. tftp_server_vrf - VRF through which the TFTP server can be reached from the switch. The default value is mgmt VRF.
        3. tftp_configuration_format - Format in which the configuration is to be copied. Valid values are cli and json. The default value is json.
        4. tftp_config_file_name_prefix- The prefix for the filename in which the configuration is copied in the TFTP server. Timestamp is appended to the prefix to generate the file name.

The script defines Monitor Resource URI(s), Monitor condition and Action:

- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
        1. Rate of system last configuration time over 10 seconds.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Conditions:  Rate of system last configuration time over 10 seconds is greater than zero.
- Clear condition: Rate of system last configuration time is equal to zero. 
- Actions:  
    - When the monitoring condition specified is hit, the following action is executed:
        - Store the last checkpoint (if available) in a script variable called 'base_checkpoint'. If the last checkpoint is not available, the 'base_checkpoint' is startup-config.
    - When the clear condition specified is hit, the following actions are executed:
        - CLI to show system is executed.
        - Syslog command saying configuration change has happened.
        - CLI to show the diff of last checkpoint and running config is executed.
        - CLI to show the diff of start-up config and running config is executed.
        - Shell command to show recent audit logs for configuration changes is executed.
        - CLI to copy the running-configuration to a TFTP server.

_Note: For very large configurations, there is a chance errors occur in the actions
of this agent due to NAE resource limitations._

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
