#!/bin/bash
# Run the declared WIDE95 gate cohort (GATE-DECLARATION.json): one label, batches 0..32767,
# candidate + two parents on identical inputs. Rows are kept whatever the verdict.
set -euo pipefail
root=/home/hclau/ecdsa_research/wide95-native-20261017
cd "$root"
echo $$ > gate-census.pid
trap 'echo $? > /home/hclau/ecdsa_research/wide95-native-20261017/gate-census.exit' EXIT
bin=/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2
echo "790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66  $bin" | sha256sum -c
echo "7c0ac9588dbf3aa90967315923778c9b3ccb954aae34bb71fc6c7bb970523109  candidate/ops.bin" | sha256sum -c
echo "1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77  /home/hclau/ecdsa_research/wide15-record-20261016/evidence/final-ops.bin" | sha256sum -c
echo "01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740  /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin" | sha256sum -c
python3 /home/hclau/ecdsa_research/server-preflight.py > gate-preflight.json
L=wide95-gate-20261017-v1
$bin candidate/ops.bin $L 0 32768 12 gate-candidate.jsonl 0 > gate-candidate.log 2>&1 &
p1=$!
$bin /home/hclau/ecdsa_research/wide15-record-20261016/evidence/final-ops.bin $L 0 32768 12 gate-parent-record.jsonl 0 > gate-parent-record.log 2>&1 &
p2=$!
$bin /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin $L 0 32768 12 gate-parent-plain67.jsonl 0 > gate-parent-plain67.log 2>&1 &
p3=$!
wait $p1; wait $p2; wait $p3
python3 gate.py > gate.log 2>&1
