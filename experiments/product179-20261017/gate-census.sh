#!/bin/bash
# Run the declared PRODUCT179 gate cohort (GATE-DECLARATION.json): label product179-gate-20261017-v1,
# batches 0..32767, candidate + the official PLAIN67 record stream on identical inputs.
set -euo pipefail
root=/home/hclau/ecdsa_research/product179-native-20261017
cd "$root"
echo $$ > gate-census.pid
trap 'echo $? > /home/hclau/ecdsa_research/product179-native-20261017/gate-census.exit' EXIT
bin=/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2
parent=/home/hclau/ecdsa_research/plain67-final-20261016/native-selected.ops.bin
echo "790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66  $bin" | sha256sum -c
echo "f2279f98d631113bf045f7d2c8f17cbc514d77a135e14234b983d4534057b78d  $parent" | sha256sum -c
python3 -c "import json;d=json.load(open('NATIVE_IDENTITY.json'));assert d['status']=='NATIVE_BYTE_IDENTITY_PASS'"
echo "$(python3 -c "import json;print(json.load(open('NATIVE_IDENTITY.json'))['expected'])")  candidate/ops.bin" | sha256sum -c
python3 /home/hclau/ecdsa_research/server-preflight.py > gate-preflight.json
L=product179-gate-20261017-v1
$bin candidate/ops.bin $L 0 32768 16 gate-candidate.jsonl 0 > gate-candidate.log 2>&1 &
p1=$!
$bin $parent $L 0 32768 16 gate-parent.jsonl 0 > gate-parent.log 2>&1 &
p2=$!
wait $p1; wait $p2
python3 gate.py > gate.log 2>&1
