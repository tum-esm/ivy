#!/bin/bash

# fail on first error
set -e errexit

# stops the mosquitto broker
pkill -f "mosquitto -d"