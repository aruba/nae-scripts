#### Script File Name: power\_supply\_monitors.2.0.PY

### SUMMARY
The System Power Supply Status monitoring script is intended to monitor the status and the value of all the Power Supply Units (PSU).

The valid PSU states are ‘ok’, ‘fault_output’ (Output Fault), ‘fault_input’ (Input Fault), ‘warning’, ‘unknown’, ‘unsupported’ and ‘fault_absent’ (Absent).   

### PLATFORM(S) SUPPORTED
8400X

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.0001

### SCRIPT DESCRIPTION
The main components of the Hardware Diagnostic "power_supply_monitor.2.0.py" script are Manifest and the Policy Constructor.   

The  'Manifest' defines the unique name for this script.

The 'Policy Constructor' handles the main logic for monitoring the status and the value of the power supply units.  

The script monitors the transition of the status

from ok to fault_input
from ok to fault_output
from ok to warning
from ok to unknown
from ok to fault_absent
from fault_output to ok
from fault_input to ok
from unknown to ok
from fault_absent to ok
When there is a transition the agent displays the output from the 'show environment power-supply' command and creates a Syslog message with the transition details.

The script also monitors and displays the maximum power and the instantaneous power in Watts for all the PSUs.


### LICENSES
Apache License, Version 2.0

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)
