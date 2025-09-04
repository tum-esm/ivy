#!/bin/bash

# tests will run in a temporary directory to not interfere with the local dev environment
export TS="$(date +%s)"
export IVY_ROOT_DIR="/tmp/ci-tests-ivy-root-dir-$TS"
mkdir $IVY_ROOT_DIR
echo "Running quick tests in temporary directory $IVY_ROOT_DIR"

# parent directory of the `README.md` file
export PROJECT_DIR=$(dirname $(dirname $(realpath $0)))
source $PROJECT_DIR/.venv/bin/activate

# runs the quick tests and kills all python processes afterward to avoid hanging processes
pytest --verbose -m "quick or updater" --cov=$PROJECT_DIR/src --exitfirst tests/
rm -rf /tmp/ci-tests-ivy*
pkill -f "Python"