#!/bin/bash

# fail on first error
set -e errexit

# parent directory of the `README.md` file
export PROJECT_DIR=$(dirname $(dirname $(realpath $0)))

# generates a password file for mosquitto
mosquitto_passwd -c -b $PROJECT_DIR/tests/updater/data/mosquitto.passwords test_username test_password

# configures the mosquitto broker
echo "listener 1883\\nallow_anonymous false\\npassword_file $PROJECT_DIR/tests/updater/data/mosquitto.passwords" > $PROJECT_DIR/tests/updater/data/mosquitto.conf

# starts the mosquitto broker in the background
mosquitto -d -c $PROJECT_DIR/tests/updater/data/mosquitto.conf