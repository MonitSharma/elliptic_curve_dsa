#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=cache-certificate-retry-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
while [ ! -f cache-certificate-parallel-20261016/launcher.exit ] || [ ! -f wide43-scratch-20261016/launcher.exit ];do sleep 30;done
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 retry_cache_certificate.py > "$out/chain.log" 2>&1
