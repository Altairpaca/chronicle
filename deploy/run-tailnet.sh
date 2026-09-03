#!/usr/bin/env bash
set -euo pipefail

chronicle_root="${CHRONICLE_ROOT:-/opt/chronicle}"
chronicle_port="${CHRONICLE_PORT:-8787}"
tailnet_ip="$(/usr/bin/tailscale ip -4 | head -n 1)"

if [[ -z "$tailnet_ip" ]]; then
  echo "Tailscale IPv4 address not available" >&2
  exit 1
fi

exec /usr/bin/python3 "$chronicle_root/server.py" \
  --host "$tailnet_ip" \
  --port "$chronicle_port" \
  --database "$chronicle_root/data/chronicle.sqlite3"
