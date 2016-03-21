#!/bin/bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

set -x
set -e

apt-get update
xargs apt-get install -y --force-yes --no-install-recommends < ${BASEDIR}/packages.txt

# cleanup
rm -rf /var/lib/apt/lists/*
apt-get clean
