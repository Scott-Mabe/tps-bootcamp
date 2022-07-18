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


