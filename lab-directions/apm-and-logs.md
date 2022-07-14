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

