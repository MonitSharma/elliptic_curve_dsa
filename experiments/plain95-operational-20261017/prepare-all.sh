#!/bin/bash
# Build, audit, gate, accept and control for the PRODUCT95 search (no search is started here).
set -euo pipefail
cd /home/hclau/ecdsa_research/plain95-operational-20261017
echo $$ > prepare-all.pid
trap 'echo $? > prepare-all.exit' EXIT
bash build.sh
python3 audit_tool_diff.py > audit.log 2>&1
python3 accept.py > accept.log 2>&1
ulimit -v 12582912
python3 control.py > control.log 2>&1
