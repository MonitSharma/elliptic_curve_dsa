#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-linear-witness-controls-20261020
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
sha256sum *.py *.rs run.sh BINDING.json > SOURCE.sha256
python3 run.py
