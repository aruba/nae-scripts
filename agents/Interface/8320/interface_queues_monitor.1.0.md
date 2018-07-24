#### Script File Name: interface\_queues\_monitor.1.0.py

### SUMMARY
The intent of this script is to monitor egress queues of an interface including the counters of Tx bytes, Tx packets & Tx errors. 8400 is an aggregation/core switch, and it is necessary to create an easy monitoring mechanism on certain critical interfaces so that the time series chart serves for visualization of queue congestion and packet loss/error.

### PLATFORM(S) SUPPORTED
8400X
8320

### MINIMUM SOFTWARE VERSION REQUIRED
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of Interface Queue monitor script are Manifest, Parameter Definition and the Policy Constructor.

The 'Manifest' defines the unique name for this script.

'ParameterDefinitions' has "interface_id" as the parameter intended to take the input from the user for monitoring the respective Interface. The default value is set to "1/1/1".

The script handles the main logic for monitoring the egress queues of an interface.

The script does not have any Rules or Thresholds since they are fully trusted to be handled by the switch inherently.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
