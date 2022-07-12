#!/bin/bash

DIR="/home/ubuntu/docker/ecommerce-workshop/traffic"
LOG_FILE="${DIR}/status.log"
PID_FILE="${DIR}/status.pid"
USER_AGENT="Mozilla/4.05 [en] (X11; U; Linux 2.0.32 i586)"
URL=http://localhost:8080
LIST=(/t/bags \
/t/clothing \
/cart \
/products/datadog-tote \
/cart?variant_id=1 \
/products/datadog-bag \
/cart?variant_id=2 \
/login)

if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2> /dev/null ; then
   echo "Process $(cat "$PID_FILE") is already running"
   exit 1
fi

count=0
echo "Generate traffic to web app"
echo "Generate traffic to web app" &> $LOG_FILE

for i in {1..240}
do
   for p in "${LIST[@]}"
   do 
      count=$((count+1))
      curl -s -o /dev/null -A "${USER_AGENT}" -w "$count: %{http_code} ${URL}$p\n" "${URL}$p" &>> $LOG_FILE
      count=$((count+1))
      curl -s -o /dev/null -A "${USER_AGENT}" -w "$count: %{http_code} ${URL}\n" "${URL}" &>> $LOG_FILE
      sleep 2
   done
done &

pid=$!

echo $pid > $PID_FILE

echo "PID of this process: $pid"
echo "pid written to $PID_FILE"
