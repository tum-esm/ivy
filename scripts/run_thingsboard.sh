#!/bin/bash

# fail on first error
set -e errexit

# parent directory of the `README.md` file
export PROJECT_DIR=$(dirname $(dirname $(realpath $0)))

# directories for persistent ThingsBoard data and logs
export DATA_DIR="$PROJECT_DIR/tests/updater/data/local_tb_data"
export LOGS_DIR="$PROJECT_DIR/tests/updater/data/local_tb_logs"

# removes any existing thingsboard container
docker rm -f mytb > /dev/null 2>&1

# runs a new thingsboard container with persistent data and log storage
docker run -it --name mytb --restart always \
    -p 9090:9090 -p 1883:1883 -p 7070:7070 -p 5683-5688:5683-5688/udp \
    -v $DATA_DIR:/data -v $LOGS_DIR:/var/log/thingsboard \
    thingsboard/tb-postgres:3.7.0