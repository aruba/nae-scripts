#### Script File Name: temp\_sensor\_status\_transition\_monitor.1.0.py

### SUMMARY
This Temperature Sensor Monitor script is intended to monitor the sensor status transition among various supported states for all available temperature sensors.

### PLATFORM(S) SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
1. The main components of the Hardware Diagnostic "temp_sensor_status_transition_monitor.1.0.py" script are the Manifest and the Policy Constructor.   

2. The 'Manifest' defines the unique name for this script .  

3. The 'Policy Constructor' handles the main logic for monitoring the status transition of all Temperature Sensors.

The supported status are: Uninitialized, Normal, Fault, Critical, Min, Max, Low_Critical, Emergency

Conditions are defined to verify the various state transitions as defined below:
- from Normal to Min/Max and vice-versa.
- from Min to Low_Critical and vice-versa
- from Max to Critical and vice-versa
- from Critical to Emergency and vice-versa
- from Fault to any of (Min/Max/Normal/Low_Critical/Critical/Emergency states) and vice-versa

When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command ('show system temperature') is displayed in the Alert Window, and the policy Status is changed as per transition state severities. The various transitioned states are represented in the time series graph/chart as well.

### LICENSES
Apache License, Version 2.0  

### REFERENCES
[Aruba Networks](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)  
