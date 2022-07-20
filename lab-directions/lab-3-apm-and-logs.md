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

# Instrument the store-frontend service 

The store-frontend service uses ruby 

Let's instapect the deploy file to learn more about the application.  

`cd ~/docker/ecommerce-workshop/deploy`

`cat docker-compose-int.yml`

You should see the following 

```
store-frontend:
    container_name: store-frontend
    environment:
      - DD_AGENT_HOST=agent
      - DD_LOGS_INJECTION=true
      - DD_PROFILING_ENABLED=true
      - DD_RUNTIME_METRICS_ENABLED=true #enable runtime metrics collection
      - DD_ENV=dev
      - DD_SERVICE=store-frontend
      - DD_VERSION=${STORE_VER}
      - RAILS_HIDE_STACKTRACE=false
      - ADS_PORT=${ADS_PORT}
      - DISCOUNTS_PORT=${DISCOUNTS_PORT}
      - ADS_ROUTE=${ADS_ROUTE}
      - DISCOUNTS_ROUTE=${DISCOUNTS_ROUTE}
    image: store-frontend:${STORE_VER}
    ports:
      - "3000:3000"
    depends_on:
      - agent
      - db
      - discounts
      - advertisements
    labels:
      com.datadoghq.ad.logs: '[{"source": "ruby", "service": "store-frontend"}]'
      my.custom.label.team: "web"
      my.custom.label.app: "spree"
```

You can also view the example if that is easier for you [here](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/40b3b250bd0d0f8d64f1daac60aaa80ca432fe0f/docker/deploy/docker-compose-instr.yml#L59)

We're going to instrument the app now 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front`

Edit your `Gemfile` has this at the end of it as the last 4 lines

```
# Setup datadog ddtrace
gem 'ddtrace', require: 'ddtrace/auto_instrument'
gem 'dogstatsd-ruby', '~> 5.3'
gem 'google-protobuf', '~> 3.0'
```

If you need help please refer to this [link](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/c1d774b729ab4e95fd447a4f4b6de692df28db6e/docker/store-frontend/src/store-front/Gemfile#L59)

Up next we need to edit the `config.ru` file.  We will be adding the following 

```
# datadog - profiling
require 'ddtrace/profiling/preload'

run Rails.application
```
Here is the complete file for your [reference](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/store-frontend/src/store-front/config.ru)


From here we need to create the `datadog.rb` file to allow tracing

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/config/initializers`

create the `datadog.rb` file with vi or nano it should contain the following 

```
require 'datadog/statsd'
require 'ddtrace'

Datadog.configure do |c|
# This will activate auto-instrumentation for Rails
   c.use :rails, {'service_name': 'store-frontend', 'cache_service': 'store-frontend-cache', 'database_service': 'store-frontend-sqlite'}
# Make sure requests are also instrumented
   c.use :http, {'service_name': 'store-frontend'}
end
```
For reference a complete file is [here](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/store-frontend/src/store-front/config/initializers/datadog.rb) 

Now we will configure ruby for logging 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/config/environments`

We must edit the `development.rb` file so that the end of the file looks like this 

```
# Add the log tags the way Datadog expects
  config.log_tags = {
    request_id: :request_id,
    dd: -> _ {
      correlation = Datadog.tracer.active_correlation
      {
        trace_id: correlation.trace_id.to_s,
        span_id:  correlation.span_id.to_s,
        env:      correlation.env.to_s,
        service:  correlation.service.to_s,
        version:  correlation.version.to_s
      }
    }
  }

  # Show the logging configuration on STDOUT
  config.show_log_configuration = true
end
```
Hint file for [reference](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/c1d774b729ab4e95fd447a4f4b6de692df28db6e/docker/store-frontend/src/store-front/config/environments/development.rb#L110)

# Build docker image for the front end 

We will need to replace the local docker image with a new one to reflect all the changes we made 

`cd ~/docker/ecommerce-workshop/store-frontend`

`docker build . -t store-frontend:1.1` 

This will take a few minutes and may generate a depency error 

# Instrument discounts service 

We will now continue instrumenting services 

The discount service uses python we can confirm this by reading our deply file 

`cat ~/docker/ecommerce-workshop/deploy/docker-compose-int.yml` 

Let's get into intrsumenting that service 

`cd ~/docker/ecommerce-workshop/discounts-service`

We need to add `ddtrace` to the `requirements.txt` file so that it looks like this 

```
certifi==2020.12.5
chardet==4.0.0
click==7.1.2
ddtrace
Flask==1.1.2
```
Link to [example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/discounts-service/requirements.txt)

Now we need to make sure the service runs as expected and can use ddtrace 

`cd ~/docker/ecommerce-workshop/deploy/`

Now edit your `~/docker/ecommerce-workshop/deploy/docker-compose-int.yml` file to contain the following for the discount service

```
image: discounts:${DISCOUNTS_VER}
    command: ["/bin/bash", "-c", "sleep 3 ; ddtrace-run flask run --port=${DISCOUNTS_PORT} --host=0.0.0.0"]
```

Here is an example if you need [help](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/08c80d7c3f6b5e90c0b5b5f096236c6c4072f54a/docker/deploy/docker-compose-instr-brum.yml#L47)

Now we need to make sure this service can send logs 

`cd ~/docker/ecommerce-workshop/discounts-service`

Edit the `discounts.py` file 

We want to add the following so that it looks like this

```

from bootstrap import create_app
from models import Discount, DiscountType, Tracker, db

##### setup datadog to connect traces and logs #####
from ddtrace import patch_all; patch_all(logging=True)
import logging
from ddtrace import tracer

FORMAT = ('%(asctime)s %(levelname)s [%(name)s]'
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
log = logging.getLogger(__name__)
##### setup datadog to connect traces and logs #####

app = create_app()
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##### setup datadog to connect traces and logs
logging.basicConfig(level=logging.INFO, format=FORMAT)
```

Here is the example file for [rerefence and help](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/08c80d7c3f6b5e90c0b5b5f096236c6c4072f54a/docker/discounts-service/discounts.py.instr.fixed#L20)

# Build docker image for the discounts service 

Now let's build a new docker image for this service 

`cd ~/docker/ecommerce-workshop/discounts-service`

`docker build . -t discounts:1.1`

# Instrument advertisement service 

We're now going to instrument the advertisement service.  

`cd ~/docker/ecommerce-workshop/ads-service`

Edit the `requirements.txt` file it should look like below

```
certifi==2020.11.8
chardet==3.0.4
click==7.1.2
ddtrace
Flask==1.1.2
```
For [help](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/ads-service/requirements.txt)

Now we need to edit the deployment file 

`cd ~/docker/ecommerce-workshop/deploy/`

Now edit your `~/docker/ecommerce-workshop/deploy/docker-compose-int.yml` file to contain the following for the ads-service

```
image: ads:${ADS_VER}
    command: ["/bin/bash", "-c", "sleep 3 ; ddtrace-run flask run --port=${ADS_PORT} --host=0.0.0.0"]
```

Let's go back to the ads-service folder to conintue editing 

`cd ~/docker/ecommerce-workshop/ads-service`

Now lets edit `ads.py` to contain the logging info we need. By adding the following 

```

FORMAT = ('%(asctime)s %(levelname)s [%(name)s]'
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
log = logging.getLogger(__name__)
##### setup datadog to connect traces and logs #####

app = create_app()
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##### setup datadog to connect traces and logs
logging.basicConfig(level=logging.INFO, format=FORMAT)

@app.route('/')
def hello():
    app.logger.info("home url for ads called")
    return Response({'Hello from Advertisements!': 'world'}, mimetype='application/json')

@app.route('/banners/<path:banner>')
def banner_image(banner):
    app.logger.info(f"attempting to grab banner at {banner}")
    return send_from_directory('ads', banner)
```
If you need help refer to this [file](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/2d24d4638b14a4bfc64bd8a7f9aded6f4a485ed7/docker/ads-service/ads.py.instr.fixed#L13) 


# Build docker image for the ads service 

Now we need to build a new image for the ads service

`cd ~/docker/ecommerce-workshop/ads-service`

`docker build . -t ads:1.1`

# Deploy time!! 

`cd ~/docker/ecommerce-workshop/deploy`

Let's be sure to edit our docker-compose file to have everything it needs for ads and discounts

We need to add the following to `docker-compose-int.ym`

First ads needs to look like this 

```
advertisements:
    container_name: ads
    environment:
      - FLASK_APP=ads.py
      - FLASK_DEBUG=1
      - POSTGRES_PASSWORD
      - POSTGRES_USER
      - POSTGRES_HOST=db
      - POSTGRES_DB=spree_ads
      - DD_SERVICE=ads-service
      - DD_AGENT_HOST=agent
      - DD_LOGS_INJECTION=true
      - DD_PROFILING_ENABLED=true
      - DD_RUNTIME_METRICS_ENABLED=true
      - DD_VERSION=${ADS_VER}
      - DD_ENV=dev
```

And discounts should look like this 

```
discounts:
    container_name: discounts
    environment:
      - FLASK_APP=discounts.py
      # - FLASK_DEBUG=1
      - POSTGRES_PASSWORD
      - POSTGRES_USER
      - POSTGRES_HOST=db
      - POSTGRES_DB=spree_discounts
      - DD_SERVICE=discounts-service
      - DD_RUNTIME_METRICS_ENABLED=true #enable runtime metrics collection
      - DD_AGENT_HOST=agent
      - DD_LOGS_INJECTION=true
      - DD_PROFILING_ENABLED=true
      - DD_VERSION=${DISCOUNTS_VER}
      - DD_ENV=dev
```
[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/deploy/docker-compose-instr-brum.yml)

We must edit the `.env` file to include the new image versions 1.1 it should now look like this 

```
# deploy version
STORE_VER=1.1
ADS_VER=1.1
DISCOUNTS_VER=1.1
```
Example [file](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/2d24d4638b14a4bfc64bd8a7f9aded6f4a485ed7/docker/deploy/.env#L8)

`docker-compose -f docker-compose-int.yml up -d` 

As always let's validate the deployment 

`docker ps -a` 


# This completes configuring APM and Logging 

Now we get to observe and troubleshoot using our Datadog accounts.