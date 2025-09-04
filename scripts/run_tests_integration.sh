#!/bin/bash

# parent directory of the `README.md` file
export PROJECT_DIR=$(dirname $(dirname $(realpath $0)))
source $PROJECT_DIR/.venv/bin/activate

# runs the integration tests
pytest --verbose -m "integration" --cov=$PROJECT_DIR/src --exitfirst tests/