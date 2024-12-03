# Overview


Aruba Network Analytics Engine (NAE) Scripts are troubleshooting solutions that allow the administrator to monitor data of a specific resource (protocol/system) and capture time series snapshot of various possible states that this resource can transition to.

The administrator creates scripts that are based on the NAE framework. A script indicates what data should be monitored, specifies conditions which act as triggers on the monitored data, specifies pre-defined actions (e.g. syslog, cli commands, etc) that can be executed when the condition is met, or indicate callback actions which are nothing but python functions to
be executed when the condition is met.

Once the Network Analytics Script is uploaded and instantiated, Time Series data collection will begin, based on the data that is monitored. The administrator views Time Series data associated with Network Analytics Agents as charts on the Web UI.

# Repository Structure:

### Recommended Scripts
##### Location: `recommended_scripts/`
These are the scripts recommended by HPE Aruba Networks for customers to use on their switches. These scripts have been tested and determined to add value. Below is a list of all of the scripts with a short description. You can click on each script directory to see all available versions (different versions have different firwmare support), as well as a README with a more detailed description of each script. All of these scripts can also be seen in the switch Web UI NAE script portal.

### Demo Scripts
##### Location: `demo_scripts/`
These are simple scripts that display the basic functionality of NAE, and can be used as building blocks to create new scripts.  These typically consist of simple monitors, rules, and actions that may not add significant customer value but can be useful to show the basics of NAE script writing.  (Will be added soon)

### Tools
##### Location: `tools/`
These are the tools used to update the metadata for use with the switch WebUI, as well as the auto-generated READMEs in the respository with information about each script.  