#!/usr/bin/env bash
set -uo pipefail
cd /home/hclau/ecdsa_research/wide-cache-20261015
echo $$ > parent.pid
uptime
free -g
/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wide-cache-paired-v1 0 4096 8 evidence/parent-census.jsonl
echo $? > parent.exit
