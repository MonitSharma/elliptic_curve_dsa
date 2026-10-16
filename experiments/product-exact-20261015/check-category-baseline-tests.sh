#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=category-restore-20261016
echo $$ > "$out/baseline-tests.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/baseline-check.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/baseline-test-preflight.json"
git -C tip rev-parse HEAD > "$out/baseline-revision.txt"
git -C tip status --short > "$out/baseline-status.txt"
cd tip
set +e
cargo test --release --locked --offline --bin build_circuit point_add -- --test-threads=1 > "../$out/baseline-native-tests.log" 2>&1
rc=$?
set -e
echo "$rc" > "../$out/baseline-native-tests.exit"
test "$rc" = 101
cd "$root"
python3 - <<'PY'
import hashlib,json,re
from pathlib import Path
r=Path.cwd();o=r/'category-restore-20261016'
names=[]
for name in ['baseline-native-tests.log','native-tests.log']:
    text=(o/name).read_text()
    names.append(re.findall(r'^test (\S+) \.\.\. FAILED$',text,re.M))
assert names[0]==names[1] and len(names[0])==3, names
files=['src/point_add/leapfrog.rs','src/point_add/square.rs']
same={p:hashlib.sha256((r/'tip'/p).read_bytes()).hexdigest()==hashlib.sha256((r/'candidate-product-restore-deletions'/p).read_bytes()).hexdigest() for p in files}
assert all(same.values())
(o/'baseline-failure-comparison.json').write_text(json.dumps({'same_failing_tests':names[0],'same_component_source':same,'interpretation':'All three failing tests are inherited on the unmodified original product source. The profiler requires an explicit env; divide/square component defaults expose existing arithmetic failures. Candidate construction succeeds; this comparison does not establish a full benchmark pass.'},indent=2)+'\n')
PY
python3 stream_resources.py candidate-product-restore-deletions/ops.bin > "$out/resources.jsonl"
