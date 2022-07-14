# In this lab we will configure the intergrations for the e-commerce application 

Let's start by taking down any running version of the app

`cd ~/docker/ecommerce-workshop/deploy`

`docker-compose -f docker-compose-agent.yml down`

Let's copy the docker-compse file so we can continue in a new file

`cp docker-compose-agent.yml docker-compose-int.yml` 

We will now begin preparing PostgreSQL to be used with Datadog 

`cd ~/docker/ecommerce-workshop/db` 

# Prepare the Database 

We need to make sure we can build the database service from a docker image.  

`cd ~/docker/ecommerce-workshop/deploy` 

`cat docker-compose-int.yml` 

We should see the following 

```
db:
    container_name: postgres
    image: postgres:12-alpine
    restart: always
    environment:
      - POSTGRES_PASSWORD
      - POSTGRES_USER
      - DD_ENV=dev
    volumes: 
      - ../db/initdb.sql:/docker-entrypoint-initdb.d/initdb.sql
      - ../db/dd_monitor.sql:/docker-entrypoint-initdb.d/dd_monitor.sql
    labels:
      com.datadoghq.ad.check_names: '["postgres"]'
      com.datadoghq.ad.init_configs: '[{}]'
      com.datadoghq.ad.instances: '[{"host":"%%host%%", "port":5432,"username":"datadog","password":"ddpassword"}]'
      com.datadoghq.ad.logs: '[{"source": "postgresql", "service": "postgres"}]'
      my.custom.label.team: "db"
      my.custom.label.app: "spree"
```
If it is not there we need to paste it into our yaml file.  Here is a file for reference [example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/493f9e2628a16c8bd85028f109e00360227a2f27/docker/deploy/docker-compose-instr-infra-integration.yml#L77)

Be aware that the volumes for the db service map back to the same folder where we inspected the `dd_monitor.sql` file 

# Prepare NGINX

Let's make sure we can work with NGINX by reviewing and editing the configuration files 

`cd ~/docker/ecommerce-workshop/nginx` 

We need to edit the default configuration file aka `default.conf` we need to add the following to the file 

```
location /nginx_status {
        stub_status;
        server_tokens on;
    }
```

For reference we can use this [example](https://github.com/ScottMabeDDHQ/labs-og/blob/f4ad97f39dcab938b90cde6c1905ab91c1c296fd/bootcamp/nginx/default.conf.instr#L11) 

Let's make sure can build the NGINX container 

`cd ~/docker/ecommerce-workshop/deploy` 

Now we will edit the file `docker-compose-int.yml` 

The NGINX container should be at the end of the file under the DB service.  See below for what we are adding.

``` 
nginx:
     container_name: nginx
     image: nginx:1.21.4
     restart: always
     environment:
       - DD_ENV=dev
     volumes:
       - ../nginx/default.conf:/etc/nginx/conf.d/default.conf
       - ../nginx/nginx.conf:/etc/nginx/nginx.conf
     ports:
       - "8080:8080"
     depends_on:
       - store-frontend
     labels:
       com.datadoghq.ad.check_names: '["nginx"]'
       com.datadoghq.ad.init_configs: '[{}]'
       com.datadoghq.ad.instances: '[{"nginx_status_url": "http://%%host%%:8080/nginx_status/"}]'
       my.custom.label.team: "nginx"
       my.custom.label.app: "spree"
```

For reference we can reffer to this [example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/3e8f7c0563d105a512619e6bef0da4665ed9a499/docker/deploy/docker-compose-instr-infra-integration.yml#L95)

# Complete Integration Configuration 

Now we will deploy what we created. From the deploy folder

`docker-compose -f docker-compose-int.yml up -d`

Confirm the deployment 

`docker ps -a`

Check the agent status 

`docker exec -it dd-agent agent status`

We should see statuses of OK with NGINX and postgres

