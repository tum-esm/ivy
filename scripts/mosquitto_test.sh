#!/bin/bash

# fail on first error
set -e errexit

mosquitto_pub -h localhost -p 1883 -t test/topic -u test_username -P test_password -m "hello"

if [ $? -ne 0 ]; then
    echo "Failed to publish message to Mosquitto broker"
    exit 1
fi