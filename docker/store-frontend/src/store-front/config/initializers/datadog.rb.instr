require 'datadog/statsd'
require 'ddtrace'

Datadog.configure do |c|
# This will activate auto-instrumentation for Rails
   c.use :rails, {'service_name': 'store-frontend', 'cache_service': 'store-frontend-cache', 'database_service': 'store-frontend-sqlite'}
# Make sure requests are also instrumented
   c.use :http, {'service_name': 'store-frontend'}
end
