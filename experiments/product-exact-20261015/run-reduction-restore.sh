#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=reduction-restore-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Predetermined whole-family correction: restore every70 inherited CX/CZ reduction, retaining all74 deletions and all upstream tables/anchors. Fixed4096 batches/source262144shots, new label product-reduction-restoration-20261016,4workers/source, immutable SIMDv2 hash. Component correctness/cost study only, no packet-selected rows, nonce search or record claim. Start build after guard-cache tool native tests/build terminal.' > "$out/DECLARATION.txt"
while [ ! -f guard-cache-20261016/product-128-generate.log ]; do
  if [ -f guard-cache-20261016/launcher.exit ]; then test "$(cat guard-cache-20261016/launcher.exit)" = 0; fi
  sleep 30
done
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_category_restore.py reductions > "$out/prepare.log" 2>&1
cd candidate-product-restore-reductions
cargo build --release --locked --offline --bin build_circuit > "../$out/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "../$out/generate.log" 2>&1
sha256sum ops.bin > "../$out/stream.sha256"
set +e
cargo test --release --locked --offline --bin build_circuit point_add -- --test-threads=1 > "../$out/native-tests.log" 2>&1
rc=$?
set -e
echo "$rc" > "../$out/native-tests.exit"
cd "$root"
test "$rc" = 101
python3 - <<'PY'
import json,re
from pathlib import Path
r=Path.cwd();out=r/'reduction-restore-20261016'
baseline=(r/'category-restore-20261016/baseline-native-tests.log').read_text();current=(out/'native-tests.log').read_text()
names=[re.findall(r'^test (\S+) \.\.\. FAILED$',s,re.M) for s in [baseline,current]]
assert names[0]==names[1] and len(names[0])==3,names
(out/'inherited-test-failures.json').write_text(json.dumps({'same_failures_as_unmodified_4b':names[0],'warning':'Three inherited component/default-environment test failures persist; no complete benchmark pass is claimed.'},indent=2)+'\n')
PY
python3 stream_resources.py candidate-product-restore-reductions/ops.bin > "$out/resources.jsonl"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/census-preflight.json"
exe=/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2
printf '%s %s\n' 790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66 "$exe" | sha256sum --check > "$out/executable-check.txt"
"$exe" tip/ops.bin product-reduction-restoration-20261016 0 4096 4 "$out/parent-census.jsonl" 0 > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-restore-reductions/ops.bin product-reduction-restoration-20261016 0 4096 4 "$out/candidate-census.jsonl" 0 > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_reduction_census.py > "$out/summary.out"
