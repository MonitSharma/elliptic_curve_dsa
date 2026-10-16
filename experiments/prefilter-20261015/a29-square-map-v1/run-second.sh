#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-square-map-v1/second.pid
trap 'echo $? > a29-square-map-v1/second.exit' EXIT
python3 a29-square-map-v1/prepare-second.py || exit $?
timeout 180 prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-square-map-v1/original-containing-hints.json a29-mask-v2/candidates-v3.json > a29-square-map-v1/a29-candidates.json 2> a29-square-map-v1/second.log
