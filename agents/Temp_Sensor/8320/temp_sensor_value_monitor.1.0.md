#### Script File Name: temp\_sensor\_value\_monitor.1.0.py

### SUMMARY
This Temperature Sensor Monitor script is intended to monitor the Temperature of all available Temperature Sensors.  

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX XL/TL.10.01.0001 

### SCRIPT DESCRIPTION
1. The main components of the Hardware Diagnostic "temp_sensor_value_monitor.1.0.py" script are Manifest, ParameterDefinitions and the Policy Constructor.   

2. The 'Manifest' defines the unique name for this script and 'ParameterDefinitions' has no parameters defined. 

3. The 'Policy Constructor' defines a single Monitor Resource URI to capture the temperature of all Temperature Sensors. 

This monitored data is then plotted in a time-series chart for analysis purpose. 

### PLATFORM(S) TESTED
8400X 
8320

### LICENSES
Apache License, Version 2.0  

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)   
