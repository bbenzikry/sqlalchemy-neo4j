#!/usr/bin/env bash

NEOJDBC_USER="neo4j" \
NEOJDBC_PASSWORD='PASSWORD_HERE' \
NEOJDBC_JAR='PATH_TO_JAR' \
NEOJDBC_PORT=7687 \
NEOJDBC_WARMUP="true" \
NEOJDBC_USER="neo4j" \
NEOJDBC_HOST="localhost" \
python examples/basic_use.py