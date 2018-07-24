#### Script File Name: temp\_sensor\_status\_transition\_as\_param\_monitor.py

### SUMMARY
This Temperature Sensor Monitor script is intended to monitor the sensor status transition among various supported states for all available temperature sensors. 

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001 

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "temp_sensor_status_transition_monitor.1.0.py" script are the Manifest, the Parameter Definitions and the Policy Constructor.   

The  'Manifest' defines the unique name for this script .  

The 'Parameter Definitions' has two parameters defined to indicate the source and destination transition states. The parameters are  'transition_from' and 'transition_to'.  

The 'Policy Constructor' handles the main logic for monitoring the status transition of all Temperature Sensors. 

The supported status are: uninitialized, normal, fault, critical, min, max, low_critical, emergency

Conditions are defined to verify the transition from 'transition_from' to 'transition_to' state. 

When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command ('show system temperature') is displayed in the Alert Window, and the policy Status is changed as per transition state severities. The various transitioned states are represented in the time series graph/chart as well. 

### PLATFORM(S) TESTED
8400X 
8320

### LICENSES
Apache License, Version 2.0  

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)  
