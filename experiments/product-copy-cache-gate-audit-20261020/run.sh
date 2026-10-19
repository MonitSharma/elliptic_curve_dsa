#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-copy-cache-gate-audit-20261020
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
export RESEARCH_SLOTS=1
python3 ../autonomous-20261019/preflight_v15.py > preflight.json
sha256sum audit.py run.sh > SOURCE.sha256
python3 audit.py
