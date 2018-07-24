#### Script File Name: single\_interface\_tx_rx\_monitor.2.0.py

### SUMMARY
This Interface Tx/Rx Stats Monitor script is intended to monitor the number of packets being transmitted or received and the packets dropped while transmitting on a given interface. 8400 is an aggregation/core switch, and it is necessary to create an easy monitoring mechanism on certain critical interfaces so that the time series chart serves for visualization of port level errors.

A point to note is that when the port goes down, these counters are not reset or brought back to zero. No change in counters across any of the monitored aspects indicate that the port is either operationally down or has been administratively shut down.

The underlying root cause for drops may be congestion or may be link failures/flaps, and this script does not really get to the actual root cause, but serves for quick visualization.

In this script, baseline function is included in this script as an option to specify the thresholds suitable to the network conditions.

The new clear_condition and clear_action functions are also added to prevent numerous alerts being generated and reset the alert status when the condition is cleared.

### PLATFORM(S) SUPPORTED
8400X
8320

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of Interface Tx/Rx monitor script are Manifest and the Agent constructor.

The 'Manifest' defines the unique name for this script.

The 'Agent Constructor' handles the main logic for monitoring the Tx/Rx packets transmitted and dropped for all interfaces.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
