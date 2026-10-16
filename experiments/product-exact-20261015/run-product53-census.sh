#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product53-frozen-census-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
r=Path.cwd();o=r/'product53-frozen-census-20261016';freeze=json.loads((r/'PRODUCT53_FREEZE.json').read_text());candidate=freeze['external_stream']
assert (r/'product-to53-20261016/launcher.exit').read_text().strip()=='0'
hashes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['tip/ops.bin',candidate]}
assert hashes[candidate]==freeze['external_stream_sha256']=='f26fe86f2d4b59f8d8cc2c860039814807d6b74f5ab29d78b3af6db9cb7f15a1'
assert hashes['tip/ops.bin']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
plan={'label':'product53-frozen-20261016','batches_per_source':32768,'shots_per_source':2097152,'threads_per_source':8,'baseline':'tip/ops.bin','candidate':candidate,'source_ops_sha256':hashes,'source_freeze':'PRODUCT53_FREEZE.json','native_port':'pending independently; must reproduce exact frozen stream before eligibility','selection':'Fixed before any rows: include every batch0..32767, no interim selection/stopping, stage/nonce tuning','nonce_search_performed':False,'score':None}
(o/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
PY
exe=/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2
printf '%s %s\n' 790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66 "$exe" | sha256sum --check > "$out/executable-check.txt"
"$exe" tip/ops.bin product53-frozen-20261016 0 32768 8 "$out/parent-census.jsonl" 0 > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" product-to53-20261016/product-53-retained-1024.bin product53-frozen-20261016 0 32768 8 "$out/candidate-census.jsonl" 0 > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_product53_census.py > "$out/summary.out"
