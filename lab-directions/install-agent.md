# Labs for TPS On-Boarding Bootcamp 

This guide will walk us through the step by step details on how to perform the labs.

First we will need to SSH into each machine 

Once inside the machine `cd ~/docker/ecommerce-workshop/deploy`
Then `cat docker-compose-no-agent.yml` 

This file is the barebones config file used to launch the demo app we are using today.  It does not have an agent installed.  
Observe the services 

Copy this file `cp docker-compose-no-agent.yml docker-compose-agent.yml`

Now lets edit that file please use the text editor you know best such as vi or nano.  

`nano docker-compose-agent.yml` 

or

`vi docker-compose-agent.yml`

We will paste the agent details as seen below directly under where you see 
`services:`


```
version: '3'
services:
  agent:
    container_name: dd-agent
    image: "datadog/agent:latest"
    environment:
      - DD_SITE
      - DD_API_KEY
      - DD_HOSTNAME=bootcamp-lab
      - DD_TAGS="project:bootcamp"
      ## LIVE PROCESSES
      - DD_PROCESS_AGENT_ENABLED=true
      ## DOGSTATSD
      - DD_DOGSTATSD_NON_LOCAL_TRAFFIC=true
    ports:
      - 8126:8126/tcp # for APM
      - 8125:8125/udp # for Dogstatsd
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
      - /etc/passwd:/etc/passwd:ro # LIVE PROCESSES
```

An example of a working file looks like [this](https://github.com/ScottMabeDDHQ/labs-og/blob/main/bootcamp/deploy/docker-compose-instr-infra-integration.yml) 

# Adding that to the docker-compose makes sure that the agent gets installed.  And it also sets some tags.  

Other items to note the ports for APM and Metrics. And the volumes will be used to gather information about the docker containers.  

# The next step requires us to use an API key from our Sandbox account.  

To add the API key from our account we need to edit the .env file from the deploy folder.

cd ~/docker/ecommerce-workshop/deploy

Use vi or nano to edit .env

When you're done it should look something like this 

`DD_API_KEY=myAPIkey`

Let's relaunch the app you should already be in the correct directory

`docker-compose -f docker-compose-agent.yml up -d`

Check to make sure everything is running 

`docker ps -a`

Let's generate more traffic now that we have rebuilt the application 

`cd ~/docker/ecommerce-workshop/traffic`

`./generate-traffic.sh`

Confirm this worked while in the same directory 

`tail -f status.log`

The following command will allow us to execute the agent status command from the agent docker container.

`docker exec -it dd-agent agent status`

This command should show you the last few characters of the API Key you generated.

`docker exec -it dd-agent agent status | grep key` 


