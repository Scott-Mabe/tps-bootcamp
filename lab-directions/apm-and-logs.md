# APM and Logs 

In these labs we will be working with some code for APM and Logs.

If your app is not running lets start it.

`cd ~/docker/ecommerce-workshop/deploy`

`docker-compose -f docker-compose-int.yml up -d` 

As always let's validate the deployment 

`docker ps -a` 

Now we will check the logs from each container 

`docker logs nginx` 

`docker logs store-frontend`

And so on 

We can now generate some traffic to the app 

`cd ~/docker/ecommerce-workshop/traffic`
 
`./generate-traffic.sh`

While in this directory let's be sure to check the logs 

`tail -f status.log`

Fyi the `status.log` file is created when you run the generate-traffic script 

We want to see how well the web page is or is not working.  We need to grab that url here's how to do that 

`curl http://169.254.169.254/latest/meta-data/public-hostname; echo`

This will print the fqdn of your ec2 instance.  Copy that and paste it into a web-browser ending in `:8080` 

It should look something like this 
`ec2-1-1-1-1.us-east-2.compute.amazonaws.com:8080` 

Now that we have seen the site and errors that are being generated let's resolve them using APM and Logs.

# Configure the agent for APM and Logs.  

Let's stop our running deployment.

`cd ~/docker/ecommerce-workshop/deploy`

`docker-compose -f docker-compose-int.yml down`

Let's review the deploy file 

`cat docker-compose-int.yml`

We should see that logs and APM are enabled already.  If your file does not contain this no worries I can help

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
      ## APM
      - DD_APM_ENABLED=true
      - DD_APM_NON_LOCAL_TRAFFIC=true
      ## LOGS
      - DD_LOGS_ENABLED=true
      - DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true
      - DD_CONTAINER_EXCLUDE_LOGS=name:agent
      - DD_DOCKER_LABELS_AS_TAGS={"my.custom.label.env":"env","my.custom.label.team":"team","my.custom.label.app":"app"}
```
Here is a link to an example file with everything we need [here](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/deploy/docker-compose-instr.yml) it should also be in your deploy folder already.

