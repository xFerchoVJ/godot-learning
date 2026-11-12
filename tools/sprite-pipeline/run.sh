#!/usr/bin/env sh
# Usage: ./run.sh [--stage idle|all]   (default: all). Output goes to ./output
set -e
cd "$(dirname "$0")"
mkdir -p output
docker compose build
docker compose run --rm sprite "$@"
