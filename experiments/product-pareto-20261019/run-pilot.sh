#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > pilot.pid
trap 'echo $? > pilot.exit' EXIT
while [ ! -f unwrap-parent.exit ]; do sleep 10; done
test "$(cat unwrap-parent.exit)" = 0
uptime > pilot-resources.txt
free -g >> pilot-resources.txt
python3 run-pilot.py > pilot.log 2>&1
