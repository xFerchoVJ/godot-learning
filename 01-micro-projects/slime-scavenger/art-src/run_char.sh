#!/usr/bin/env sh
# Usage: ./run_char.sh <name> [--stage <first_stage>|all]
# Runs generate_<name>.py in Docker. Output goes to ./output/<name>.
set -e
name="$1"; shift
cd "$(dirname "$0")"
mkdir -p "output/$name"
docker compose run --rm \
  -v "$PWD/generate_$name.py:/app/generate_$name.py:ro" \
  -v "$PWD/output/$name:/out" \
  --entrypoint python sprite "generate_$name.py" "$@"
