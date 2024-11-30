## Summary

Agent to alert user when configuration changes and show the system info and diff of configuration changes. An incident is created in TOPdesk, with the diff of configuration changes and other details.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.11 Minimum

## Supported Platforms

Script Version 2.0: 8320, 8325, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
        - username - Username of the TOPdesk® account instance.
        - password - Password of the TOPdesk® account instance.
        - domain_name - Domain name of the TOPdesk® account instance.
        - short_description - Short description for the configuration change event.
        - web_proxy - Web proxy IP address  

The script defines Monitor Resource URI(s), Monitor condition and Action : 

- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Rate of system last configuration time over 10 seconds.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Conditions:  This script specifies monitoring condition as following:
    1. Rate of system last configuration time over 10 seconds is greater than zero.
- Clear condition: Rate of system last configuration time is equal to zero. 
- Actions:  This script specifies monitoring action as following:  
    - When the monitoring condition (1) specified is hit, the following action is executed:
        - Store the last checkpoint (if available) in a script variable called 'base_checkpoint'. If the last checkpoint is not available, the 'base_checkpoint' is startup-config.
    - When the clear condition specified is hit, the following actions are executed:
        - CLI to show system is executed.
        - Syslog command saying configuration change has happened.
        - CLI to show the diff of last checkpoint and running config is executed.
        - CLI to show the diff of start-up config and running config is executed.
        - Shell command to show recent audit logs for configuration changes is executed.
        - An incident ticket is posted to TOPdesk®, with the configuration diff, system and time information.
        - A link to the Agent dashboard of the affected switch is provided in the ticket 

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
