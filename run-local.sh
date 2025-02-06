#!/bin/bash

# set up a running environment and fire off some payloads

DOCKER=$(which docker)
if [ -z "$DOCKER" ]; then
  DOCKER=$(which podman)
fi

set -eo pipefail

if [ -z "$LAMBDA" ]; then
  LAMBDA=$(which aws-lambda-rie)
    if [ -z "$LAMBDA" ]; then
        echo "No lambda image found, set LAMBDA env var to the path to aws-lambda-rie, or put it on your PATH"
        echo "If needed, install from https://github.com/aws/aws-lambda-runtime-interface-emulator/"
        exit 1
    fi
fi

$DOCKER build -t phonehome:test --platform=linux/amd64 .

$DOCKER run -d -p 9000:8080 \
    --entrypoint /usr/local/bin/aws-lambda-rie \
    phonehome:test ./main