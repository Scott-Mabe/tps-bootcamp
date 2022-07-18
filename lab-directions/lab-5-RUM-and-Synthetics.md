# RUM and Synthetics Lab

In these labs we will be working with RUM and Sythetics

# We're starting in the console 

In your sandbox account please go to new [RUM application page](https://app.datadoghq.com/rum/application/create)

We will be creating a JS application using CDN Sync 

The `env` and `service` identifiers can be changed if needed it's use `env:dev` and `service:spree-web-ui` 

Be sure to keep the `applicationId:` and `clientToken` available

# Connect RUM and Traces

We need to make edits to our ruby app to allow RUM to connect and gather data.

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front`

Edit the `Gemfile` 

Add the following to the Gemfile 

```
# Use rack-cors to add CORS for datadog rum and traces
gem 'rack-cors', '~> 1.0.3'
```
[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/f11675c2316be56231765a03bab878f11e0fd9ac/docker/store-frontend/src/store-front/Gemfile#L21)

Now we need to edit the `application.rb` file 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/config`

Edit `application.rb` to have the following at the end of the file 

```
# configure CORS to allow datadog rum headers
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins 'ec2*.amazonaws.com:8080'
        resource '*',
          headers: :any,
          methods: [:get, :post, :delete, :put, :options]
      end
    end
```
[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/f11675c2316be56231765a03bab878f11e0fd9ac/docker/store-frontend/src/store-front/config/application.rb#L47)


Now we must edit the Javascript to allow rum 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/app/views/layouts`

Edit the `application.rb` file to add the following 

```
<script>
      window.DD_RUM && window.DD_RUM.init({
        applicationId: '<%= ENV['DD_APPLICATION_ID'] %>',
        clientToken: '<%= ENV['DD_CLIENT_TOKEN'] %>',
        site: '<%= ENV['DD_SITE'] %>',
        service:'<%= ENV['DD_BRUM_SERVICE'] %>',
        env:'<%= ENV['DD_ENV'] %>',
        version: '<%= ENV['DD_VERSION'] %>',
        sampleRate: 100,
        trackInteractions: true,
        defaultPrivacyLevel: 'mask-user-input',
        allowedTracingOrigins: [/http:\/\/ec2.*\.amazonaws\.com:8080/]
    }); 

    window.DD_RUM &&
    window.DD_RUM.startSessionReplayRecording();
  </script>
```
[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/store-frontend/src/store-front/app/views/layouts/application.html.erb)

And now 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store- front/app/views/spree/layouts`

Edit the `application.html.erb` file to contain the following 

```
<script>
    window.DD_RUM && window.DD_RUM.init({
        applicationId: '<%= ENV['DD_APPLICATION_ID'] %>',
        clientToken: '<%= ENV['DD_CLIENT_TOKEN'] %>',
        site: '<%= ENV['DD_SITE'] %>',
        service:'<%= ENV['DD_BRUM_SERVICE'] %>',
        env:'<%= ENV['DD_ENV'] %>',
        version: '<%= ENV['DD_VERSION'] %>',
        sampleRate: 100,
        trackInteractions: true,
        defaultPrivacyLevel: 'mask-user-input',
        allowedTracingOrigins: [/http:\/\/ec2.*\.amazonaws\.com:8080/]
    });

    window.DD_RUM &&
    window.DD_RUM.startSessionReplayRecording();
  </script>
```
# Build new Docker image for the store front 

`cd ~/docker/ecommerce-workshop/store-frontend`

`docker build . -t store-frontend:1.3`

Now let's edit the `.env` file 

`cd ~/docker/ecommerce-workshop/deploy`

Edit `.env` to relect the new version which is `1.3`

Confirm the docker-compose file by reading it 

`cat docker-compose-instr-brum.yml`

Let's start the app 

`docker-compose -f docker-compose-instr-brum.yml up -d`

# Verify the install 

`curl http://169.254.169.254/latest/meta-data/public-hostname; echo` 

This will get you the public URL of your VM or use the spreadsheet 

Use the url and add :8080 to the end to see the webpage 
