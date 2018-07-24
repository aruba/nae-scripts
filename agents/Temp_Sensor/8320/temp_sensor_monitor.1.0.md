#### Script File Name: temp\_sensor\_monitor.1.0.py

### SUMMARY
This Temperature Sensor Monitor script is intended to monitor all attributes of a specified Temperature Sensor on the line card. The attributes are for monitoring the temperature value and the status of the temperature sensors.

The supported status are: Uninitialized, Normal, Min, Max, Low Critical, Critical, Fault and Emergency.

### PLATFORM(S) SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "temp_sensor_monitor.1.0.py" script are Manifest, ParameterDefinitions and the Policy Constructor.   

The  'Manifest' defines the unique name for this script and 'ParameterDefinitions' has two parameters defined as to indicate the subsystem type to which the Temperature Sensor belongs to and the Sensor Name. The parameters are 'sensor_subsystem_type' and 'sensor_name'.  

The 'Policy Constructor' handles the main logic for monitoring the status and the temperature value of the specified Temperature Sensor.  

The first Monitor Resource URI monitors the temperature value of the Temperature Sensor and  no Action is taken corresponding to this. The monitored temperature values over time are  plotted in a  time-series chart for analysis purpose.

The second Monitor Resource URI monitors the status of the specified  Temperature Sensor.

This monitored data is then plotted in a time-series chart for analysis purpose.

When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command  ('show system temperature') is displayed  in the Alert Window and the policy Status is  changed as per transition state severities. 


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
