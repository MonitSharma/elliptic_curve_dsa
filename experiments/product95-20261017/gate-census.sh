#!/bin/bash
# Run the declared PRODUCT95 gate cohort (GATE-DECLARATION.json): one label, batches 0..32767,
# candidate + two parents on identical inputs. Rows are kept whatever the verdict.
set -euo pipefail
root=/home/hclau/ecdsa_research/product95-native-20261017
cd "$root"
echo $$ > gate-census.pid
trap 'echo $? > /home/hclau/ecdsa_research/product95-native-20261017/gate-census.exit' EXIT
bin=/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2
echo "790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66  $bin" | sha256sum -c
echo "ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84  candidate/ops.bin" | sha256sum -c
echo "2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e  /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin" | sha256sum -c
echo "f2279f98d631113bf045f7d2c8f17cbc514d77a135e14234b983d4534057b78d  /home/hclau/ecdsa_research/plain67-final-20261016/native-selected.ops.bin" | sha256sum -c
python3 /home/hclau/ecdsa_research/server-preflight.py > gate-preflight.json
L=product95-gate-20261017-v1
$bin candidate/ops.bin $L 0 32768 12 gate-candidate.jsonl 0 > gate-candidate.log 2>&1 &
p1=$!
$bin /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin $L 0 32768 12 gate-parent-record.jsonl 0 > gate-parent-record.log 2>&1 &
p2=$!
$bin /home/hclau/ecdsa_research/plain67-final-20261016/native-selected.ops.bin $L 0 32768 12 gate-parent-plain67.jsonl 0 > gate-parent-plain67.log 2>&1 &
p3=$!
wait $p1; wait $p2; wait $p3
python3 gate.py > gate.log 2>&1
