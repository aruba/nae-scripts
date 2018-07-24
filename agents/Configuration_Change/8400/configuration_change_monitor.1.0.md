#### Script File Name: configuration\_change\_monitor.1.0.py

### SUMMARY
The purpose of this script is to alert the user when system configuration changes. A ticket is created in ServiceNow® with the diff of changes and other details.    

### PLATFORMS SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

### SCRIPT DESCRIPTION
The main components of the script are Manifest, Parameter Definitions and python code.  

'Manifest' defines the unique name for this script.
'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters:
username - Username of the ServiceNow® account instance.
password - Password of the ServiceNow® account instance.
domain_name - Domain name of the ServiceNow® account instance.
short_description - Short description for the configuration change event.
web_proxy - Web proxy IP address
urgency - Urgency of the configuration change event.
severity - Severity of the configuration change event.
The script defines Monitor Resource URI(s), Monitor condition and Action :

Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
Rate of system last configuration time over 10 seconds.

Note: The monitored data is plotted in a time-series chart for analysis purpose.  

Conditions:  This script specifies monitoring condition as following:
Rate of system last configuration time over 10 seconds is greater than zero.
Clear condition: Rate of system last configuration time is equal to zero.
Actions:  This script specifies monitoring action as following:  

When the monitoring condition (1) specified is hit, the following action is executed:
Store the last checkpoint (if available) in a script variable called 'base_checkpoint'. If the last checkpoint is not available, the 'base_checkpoint' is startup-config.
When the clear condition specified is hit, the following actions are executed:
CLI to show system is executed.
Syslog command saying configuration change has happened.
CLI to show the diff of last checkpoint and running config is executed.
CLI to show the diff of start-up config and running config is executed.
Shell command to show recent audit logs for configuration changes is executed.
A ticket is posted to the Incident table of ServiceNow®, with the configuration diff, urgency, severity, short description, category (network) and time information.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
