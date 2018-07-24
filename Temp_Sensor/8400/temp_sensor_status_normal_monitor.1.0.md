#### Script File Name: temp\_sensor\_status\_normal\_monitor.1.0.py 

### SUMMARY
This script monitors the status of all the temperature sensors. 

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic  "temp_sensor_status_normal_monitor.1.0.py" script are Manifest and the Policy Constructor.  

The  'Manifest' defines the unique name for this script. 

The 'Policy Constructor' handles the main logic for monitoring the specific status of all the Temperature Sensors.

The supported status are: Uninitialized, Normal, Min, Max, Low Critical, Critical, Fault and Emergency. 

The agent is in normal state when the status of the sensors is Max, Min, Uninitialized or Normal. The agent goes into critical state when the status of the sensors is Critical, Low Critical, Emergency or Fault.

When the agent enters the critical state, a syslog message is created and the output of the command 'show environment temperature' is displayed in the UI. 

### PLATFORM(S) TESTED
8320
8400X

### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine) 
