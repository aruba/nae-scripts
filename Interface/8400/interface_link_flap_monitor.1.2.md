#### Script File Name: interface\_link\_flap\_monitor.1.2.py

### SUMMARY
This Interface Link Flap Monitor script is intended to monitor link flap happening on any interface on the switch. Link flapping is a scenario where an interface toggles continuously between “up” and “down” states which is also known as “link resets”.

This script monitors the rate of link resets happening over the defined time interval. If the rate increases beyond the specified threshold then the following actions are taken:
- Agent status is set to Critical.
- Syslog messages are written indicating the link flap happening on the particular interface.

Critical state of the script agent indicates the link flap happening on an interface. And by looking at the syslog message or alert details user can figure out on which exact interface the flap is happening. 

In this script, clear_condition is added to prevent numerous alerts that can occur when link flap happening and the clear_action is added to reset the alert status when the condition is cleared.

### MINIMUM SOFTWARE VERSION REQUIRED 
ArubaOS-CX XL/TL.10.01.0001

### CONFIGURATION NOTES
The important section of interface link flap monitor script are Manifest, Parameter Definition and the actual python code.

The 'Manifest' defines the unique name for this script and the 'ParameterDefinitions' section defines the following script parameters:

- 'link_flap_threshold' -> specifies the link state resets per second, that is an anomalous level for the link. The default value is 0.1.
The script handles the main logic for monitoring the flapping links.

Condition is defined to monitor 'link_resets' count of all interfaces. 'link_resets' specifies the number of times Switch has observed the link state change from "up" to "down".

If the rate of 'link_resets' count over the time interval 'rate_interval' (specified in the parameter) increases beyond the specified threshold 'link_flap_threshold' then an the following actions are taken :

1. Agent status is set to Critical.
2. Syslog messages are written indicating the link flap happening on the particular interface.

And when the rate of 'link_resets' count over the time interval 'rate_interval' falls below the specified threshold 'link_flap_threshold' then the agent status is set back to Normal.

### PLATFORM(S) TESTED
8400X
8320

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
