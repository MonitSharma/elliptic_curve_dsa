#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/all70-value-transfer-20261016
trap 'rc=$?; echo "$rc" > supplement.exit' EXIT
ulimit -v 16777216
python3 primitive-checks.py
python3 refine-swap.py
