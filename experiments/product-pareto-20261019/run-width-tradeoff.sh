#!/bin/bash
set -euo pipefail
ulimit -c 0
r=/home/hclau/ecdsa_research/product-pareto-20261019
out=/home/hclau/ecdsa_research/product-width-tradeoff-20261019
cd "$r"
test ! -e width-tradeoff.pid
echo $$ > "$r/width-tradeoff.pid"
trap 'echo $? > "$r/width-tradeoff.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 prepare_width_tradeoff.py
cd "$out"
ulimit -v $((64*1024*1024))
cargo test --release --offline > tests.log 2>&1
cargo build --release --offline > build.log 2>&1
echo '99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683  /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin' | sha256sum -c > input-check.log
target/release/width_pressure "$r/parent/ops.bin" parent-width.json > parent-width.log 2>&1
target/release/tradeoff "$r/parent/ops.bin" all-exact-recomputed 1024 > discovery.log 2>&1
target/release/width_pressure all-exact-recomputed.ops.bin recomputed-width.json > recomputed-width.log 2>&1
python3 - <<'PY'
from pathlib import Path
import hashlib,json
r=Path.cwd();p=json.loads((r/'parent-width.json').read_text());c=json.loads((r/'recomputed-width.json').read_text());m=json.loads((r/'all-exact-recomputed.json').read_text())
v={'status':'WIDTH_TRADEOFF_DIAGNOSTIC_COMPLETE_NOT_A_RECORD','parent_conservative_peak':p['peak_simultaneous_lifetimes'],'recomputed_conservative_peak':c['peak_simultaneous_lifetimes'],'removed_caches':len(m['unwrappings']),'predicted_added_T':m['predicted_additional_toffoli'],'candidate_emitted':False,'nonce_search':False,'next':'If the peak falls, select a lower-cost exact removal subset and implement interval recoloring; otherwise record the negative and change method.'}
(r/'RESULT.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
PY
