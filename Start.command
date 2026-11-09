#!/bin/bash
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
cd "$(dirname "$0")" || exit 1
docker info >/dev/null 2>&1 || { open -a Docker; for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 2; done; }
docker compose up --build -d
for i in $(seq 1 40); do curl -s -o /dev/null http://localhost:8102/ && break; sleep 1; done
open -a Safari http://localhost:8102
echo "PhishLens -> http://localhost:8102  (stop: docker compose down)"
