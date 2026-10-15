#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide-quadratic-factor-20261016
echo $$ > controls.pid
trap 'echo $? > controls.exit' EXIT
ulimit -v 16777216
/usr/bin/time -v python3 controls.py > controls.log 2>&1
