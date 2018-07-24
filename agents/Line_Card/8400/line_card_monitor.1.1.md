#### Script File Name: line\_card\_monitor.1.1.py

### SUMMARY
The intent of this script is to monitor health of all the Line cards (LC) on the switch. Agent monitors line card state, CPU and Memory utilization. In case, any line card is down, agent collects corresponding line card logs and executes switch CLI commands which help to know the cause of line card failure.

### PLATFORM(S) SUPPORTED
8400x

### SOFTWARE VERSION REQUIREMENTS
ArubaOS-CX 10.01.000X

### SCRIPT DESCRIPTION
The sections of this script are 'Manifest', 'ParameterDefinitions' and the 'Policy Constructor'.

#### 'Manifest' defines the unique name for this script.

#### 'ParameterDefinitions' section defines script parameters. In this script, there are no parameters.

The 'Agent Constructor' handles the main logic for monitoring state, CPU/Memory utilization of all line cards on the switch. State, CPU and Memory utilization of all line cards will be presented to the user in single time series chart. User can customize the chart to select the line card monitors that needs to be presented since max monitors that are presented are 8. Single condition is defined to check whether any line card is in 'down' state. If any line card is in 'down' state, actions are taken by the agent.

The python code defines following monitor(s) (Resource URI), condition(s) and action(s) :

#### Monitor(s):
            1. all line card state, URI - '/rest/v1/system/subsystems/line_card/*?attributes=state'

            2. all line card CPU, URI - '/rest/v1/system/subsystems/line_card/*?attributes=resource_utilization.cpu'

            3. all line card Memory, URI - '/rest/v1/system/subsystems/line_card/*?attributes=resource_utilization.memory'

#### Condition(s):
            1. line card state is equal to ‘down’

#### Action(s):
            1. Set agent status to Critical

            2. Line card details are logged to Syslog that is in down state

            3. Execute following CLI/Shell commands:

                         -  CLI : 'show mod <lc_slot>'

                         -  CLI : 'show events -d hpe-cardd'

                         -  Shell : 'ovs-appctl -t hpe-cardd fastlog show lc <lc_number>'

Agent alerts for each and every line card failure (i.e. in down state) on the switch. Also Agent generates clears earlier alert in case line card comes back from 'down' state.


### LICENSES
Apache License, Version 2.0  

### REFERENCES
[Aruba Networks Community](http://community.arubanetworks.com/t5/Network-Analytic-Engine/ct-p/NetworkAnalyticEngine)  
