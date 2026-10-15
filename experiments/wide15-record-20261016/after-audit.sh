#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide15-record-20261016
echo $$ > after-audit.pid
trap 'rc=$?; echo "$rc" > after-audit.exit' EXIT
while test ! -f qualify.exit; do sleep 10; done
test "$(cat qualify.exit)" = 0
python3 audit-prefix.py > prefix-audit.log 2>&1
