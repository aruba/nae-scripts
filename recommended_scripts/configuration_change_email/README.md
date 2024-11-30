## Summary

Agent to alert user when configuration changes and show the system info and diff of configuration changes. An email notification with the diff is sent whenever the configuration changes.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.0: 8320, 8325, 8400

## Script Description

- 'Parameter Definitions' defines the input parameters to the script.  
    This script requires the following parameters:  
        1. smtp_server_address - IP address and port of the SMTP server.  
           Example \<IP address\>:\<Port\> or \<Hostname\>:\<Port\>
        2. sender_email_address - Optional parameter which is used to specify the email address from which the email alert is to be sent.
        3. recipient_email_address - Comma separated list of email addresses to which the email alert must be sent.
        4. smtp_server_user_id - Optional parameter which can be used to specify the SMTP server user name incase the SMTP server is protected with username and password.
        5. smtp_server_user_password - Optional parameter which can be used to specify the SMTP server password incase the SMTP server is protected with username and password.  
        6. email_subject - Optional parameter which can be used to specify the subject of the email alert sent whenever there is a configuration change.  If it left empty, a default value of 'NAE detected a config change event' will be used as the subject of the email.
        7. switch_host_name - Optional parameter which can be used in the SMTP helo/ehelo messages. If left blank, the hostname of the switch along with the switch domain name.

The script defines Monitor Resource URI(s), Monitor condition and Actions : 

- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
        1. Rate of system last configuration time over 10 seconds.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Conditions:  Rate of system last configuration time over 10 seconds is greater than zero.
- Clear condition: Rate of system last configuration time is equal to zero. 
- Actions:
        - When the monitoring condition specified is hit, the following action is executed:
            - Store the last checkpoint (if available) in a script variable called 'base_checkpoint'. If the last checkpoint is not available, the 'base_checkpoint' is startup-config.
        - When the clear condition specified is hit, the following actions are executed:
            -CLI to show system is executed.
            - Syslog command saying configuration change has happened.
            - CLI to show the diff of last checkpoint and running config is executed.
            - CLI to show the diff of start-up config and running config is executed.
            - Shell command to show recent audit logs for configuration changes is executed.
            - An email alert is sent with the configuration diff.
            - A link to the Agent dashboard of the affected switch is provided in the email alert.

_Note: For very large configurations, there is a chance errors occur in the actions of this agent due to NAE resource limitations.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
