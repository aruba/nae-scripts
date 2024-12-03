## Summary

This script monitors the overall hardware device health.

## Supported Software Versions

Script Version 1.6: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 1.6: 6200, 6300, 64xx, 8100, 8320, 8325, 8360, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and python code. 
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - rx_crc_err_threshold: Threshold for bad cable fault
    - ethernet_fragments_threshold: Threshold for bad transceiver fault
- Monitors:  This script specifies the monitoring URI(s) to monitor the following: 
    - Temperature sensor status
    - Fan Status
    - Rate of interface good frames (packets/s)
    - Rate of Rx CRC error packets (packets/s)
    - Rate of ethernet stats fragments error packets (packets/s)
- Actions:  This script performs the following actions:
    - For temperature sensor, When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command  ('show system temperature') is displayed  in the Alert Window and the policy Status is  changed as per transition state severities. 
    - The 'Agent Constructor' handles the main logic for monitoring the 'fault' status of all Fans. Conditions are defined such that when there is a transition from one status value to another value, the agent executes a action callback for it. Status values like empty/uninitialized/ok are considered to be normal status of a fan and other states like fault is considered to be critical status value of a fan. A data structure named 'fans_list' is used to list fans which transited to critical status. 
    - When any fan transit from normal status(empty/uninitialized/ok) to critical status(fault), then the callback 'fans_status_action_fault' is invoked.  The variable 'fans_list' is updated with that fan name and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name. Upon next fan transit to fault status, the agent displays CLI and syslog with that fan name.   
    - When the fan in faulty status(fault) transit to normal status values(empty/uninitialized/ok), the fan name in 'fans_list' is removed.When all the fans status are set back to any normal status values and 'fans_list' is empty, the agent status is set back to 'Normal'.
    - Fault Finder, when rate of ethernet stats fragments error packets (packets/s) is above the threshold:
        - The agent status is marked as critical & syslog message displayed.
    - When rate of Rx CRC error packets (packets/s) is above the threshold:
        - The agent status is marked as critical & syslog message displayed.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
