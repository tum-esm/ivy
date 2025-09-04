#!/bin/bash

# stops the mosquitto broker
pkill -f "mosquitto -d" || true