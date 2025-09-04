#!/bin/bash

# fail on first error
set -e errexit

# parent directory of the `README.md` file
export PROJECT_DIR=$(dirname $(dirname $(realpath $0)))

# generates a password file for mosquitto
mosquitto_passwd -c -b $PROJECT_DIR/tests/updater/data/mosquitto.passwords test_username test_password

# configures the mosquitto broker
cat > $PROJECT_DIR/tests/updater/data/mosquitto.conf << EOF
listener 1883
allow_anonymous false
password_file $PROJECT_DIR/tests/updater/data/mosquitto.passwords
EOF

# starts the mosquitto broker in the background
mosquitto -d -c $PROJECT_DIR/tests/updater/data/mosquitto.conf