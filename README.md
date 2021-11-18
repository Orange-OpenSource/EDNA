# EDNA
Event-Driven Network Automation (edna) is a solution built with Salt and Napalm that allows the automation of reactions triggered by specific events that take place in a network.

The solution has three components: *salt-master*, *salt-minion*, and *salt-proxy*. Salt-master plays the roles of orchestrator, salt-minion serves as the orchestrators suport to receive, organize, and detect events; finally *salt-proxy* connects to network devices in order to deploy the changes in the configurations passed by the orchestrator.

### Requirements:
You need to install `Docker` and `docker-compose` in your machine. The latest version of EDNA runs over Docker version 20.10.2 and docker-compose version 1.25.0.

The procedures explained below were done on a Ubuntu 20.04 machine. The commands shown might vary depending on your operating system.


### Files

#### Project folder
***buildUp.py***: This file builds container images based on Dockerfile-master, Dockerfile-minion, Dockerfile-proxy.
***startUp.py***: This files starts up EDNA solution.

#### salt-master
***EDNA/master_files/srv/(all files)***: Salt configuration files needed to start up salt-master and configure EDNA monitoring and response with Salt.

#### salt-minion
***EDNA/minion_files/minion***: Salt configuration file needed to start up salt-minion.

***EDNA/minion_files/edna/fileDiff.py***: monitor files network_events and response_action.

***EDNA/minion_files/edna/network_events***: Stores events that are deployed in the network. This file is used for triggering network events when testing the solution.

***EDNA/minion_files/edna/response_action***: Stores events that trigger a response from EDNA.

#### salt-proxy
***EDNA/proxy_files/proxy***: Salt configuration file needed to start up salt-proxy.

### Bringing everything up
To start the solution use the command `python3 startUp.py 1`. This will start a salt-master, salt-minion, and one salt-proxy machine. The number 1 passed as argument is the number of salt-proxies to be used

After exceuting the previous command you will have running the infrastructure shown the image below:

```
		+----------+               +------------+
		|          |<--------------+            |
		|  Minion  |    net-3      |   Master   |
		|          +-------------->|            |
		+----------+               +----+-------+
				                |   ^
				                |   |
				                |   |
				         net-2  |   |
				                |   |
				                |   |
				                v   |
				            +-------+---+
				            |           |
				            |  Proxy0   |
				            |           |
				            +---+-------+
				                |   ^
				          net-a |   |
				                |   |
				                v   |
				        +-----------+-------+
				        |                   |
				        |  Network device   |
				        |                   |
				        +-------------------+
```

### Testing the solution
Connect to the `salt-master` using the command salt 'proxy0' net.cli "show running-config. Run the command ``salt "*" test.ping``. This command verifies the connectivity to al;l the device connected to the master. You should a positive response from the `salt-minion` and a negative one from the `salt-proxy`. This negative response is due to no network device is connected to the proxy.

To try more complex commands you can deploy a router (network device) in a docker container and connect it to the net-a network. You can check the drivers available in https://napalm.readthedocs.io/en/latest/support/. Then configure the IP, port, username and password to login the router in the file `master_files\srv\pillar\proxy0.sls`.

Finally, you can test the connection to the router by running again the test ping command from the salt-master. To get specific information from the router device you can use the net.cli command and target proxy0, for instance: `salt 'proxy0' net.cli "show running-config`.


### Bringing the solution down
Use the command ``docker stop $(docker ps -q)`` to bring the solution down.
