## Summary

Agent to alert user when configuration changes and show the system info and diff of configuration changes. A ticket is created in Incident table of ServiceNow, with the diff of configuration changes and other details.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.11 Minimum

## Supported Platforms

Script Version 2.0: 8320, 8400

## Script Description

- 'Parameter Definitions' defines the input parameters to the script.  
This script requires the following parameters: 

    1. username - Username of the ServiceNow® account instance.
    2. password - Password of the ServiceNow® account instance.
    3. domain_name - Domain name of the ServiceNow® account instance.
    4. short_description - Short description for the configuration change event.
    5. web_proxy - Web proxy IP address
    6. urgency - Urgency of the configuration change event.
    7. severity - Severity of the configuration change event.

The script defines Monitor Resource URI(s), Monitor condition and Actions: 

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
        - A ticket is posted to the Incident table of ServiceNow®, with the configuration diff, urgency, severity, short description, category (network) and time information

_Note: For very large configurations, there is a chance errors occur in the actions of this agent due to NAE resource limitations._

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
