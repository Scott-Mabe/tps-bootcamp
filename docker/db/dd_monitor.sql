create user datadog with password 'ddpassword';
grant SELECT ON pg_stat_database to datadog;
grant pg_monitor to datadog;
