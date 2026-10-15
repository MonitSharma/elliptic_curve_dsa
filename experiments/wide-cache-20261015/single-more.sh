#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > single-more.pid
trap 'rc=$?; echo "$rc" > "$root/single-more.exit"' EXIT
ulimit -v 50331648
uptime
free -g
tool=./single-tool/target/release/product_paired_diagnostic
"$tool" single/one.bin 7 single/eight.bin > single/eight.log 2>&1
sha256sum single/eight.bin > single/eight.sha256
/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census single/eight.bin wide-cache-paired-v1 0 4096 16 single/eight-census.jsonl > single/eight-census.log 2>&1
