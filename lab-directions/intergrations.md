# In this lab we will configure the intergrations for the e-commerce application 

Let's start by taking down any running version of the app

`cd ~/docker/ecommerce-workshop/deploy`

`docker-compose -f docker-compose-agent.yml down`

Let's copy the docker-compse file so we can continue in a new file

`cp docker-compose-agent.yml docker-compose-int.yml` 

We will now begin preparing PostgreSQL to be used with Datadog 

`cd ~/docker/ecommerce-workshop/db` 

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
