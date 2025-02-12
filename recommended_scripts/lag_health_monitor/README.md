## Summary

LAG status monitoring agent using PSPO

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.04 Minimum

## Supported Platforms

Script Version 2.0: 6300, 6400, 8320, 8400

## Script Description

The main components of the script are Manifest, Parameter Definitions and the Python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    1. lag_name_1 – This parameter specifies lag name. Default value is ' '.
    2. lag_name_2 - This parameter specifies lag name. Default value is ' '.
    3. lag_name_3 - This parameter specifies lag name. Default value is ' '.
    4. lag_name_4 - This parameter specifies lag name. Default value is ' '.
    5. lag_name_5 - This parameter specifies lag name. Default value is ' '.
    6. lag_name_6 - This parameter specifies lag name. Default value is ' '.
    7. lag_name_7 - This parameter specifies lag name. Default value is ' '.
    8. lag_name_8 - This parameter specifies lag name. Default value is ' '. 

The script defines Monitor(s), Condition(s) and Action(s) : 

- Monitors:   
    1. forwarding_state - Port's forwarding state which is determined by state of the interface(s) of LAG:
        - forwarding - Summarizes the state of all the contributors that can block the Port.
        - blocking_layer - Name of the layer that is blocking the forwarding_state.
- Conditions: 
    1. Conditions are defined to verify the transition of forwarding state of configured LAG from "true" to "false" AND blocking layer from any state to "AGGREGATION" .  
- Actions:
    1. Critical alert – When the monitoring condition is met, agent status is changed to Critical. A detailed Syslog message indicating the transition states and output of CLI command ('show lacp aggregate {lag_id}') is displayed  in the monitoring agent UI. 
    2. Normal alert -  When blocking layer and forwarding state is transitioned back to "NONE" and "true" respectively, then the agent status is set back to 'Normal'.  A Syslog message indicating the LAG status is displayed in the monitoring agent UI.

This monitored data is then plotted in a time-series chart for analysis purpose.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
