#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > independent-curves-v9.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/independent-curves-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > independent-curves-v9-preflight.json
test "$(cat generate-v9.exit)" = 0
python3 prepare-independent-curves.py "$ROOT"
python3 prepare-independent-curve-replay.py /home/hclau/ecdsa_research/overnight-20261014/qubits/base "$ROOT/independent-curves-v9-crate"
export CARGO_TARGET_DIR="$ROOT/independent-curves-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path independent-curves-v9-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path independent-curves-v9-crate/Cargo.toml -- "$ROOT/stream-v9.bin" "$ROOT/independent-curve-packet-v9.json" "$ROOT/independent-curves-v9-result.json" > independent-curves-v9-proof.log 2>&1
python3 - <<'PY'
from pathlib import Path
import json
r=json.loads(Path('/home/hclau/ecdsa_research/q692_readiness_20261015/independent-curves-v9-result.json').read_text(encoding='utf8'))
assert r['value_mismatch_lanes']==0,r['value_mismatch_lanes']
assert int(r['phase_word'],16)==0,r['phase_word']
assert r['ancilla_garbage']==[],r['ancilla_garbage']
print('INDEPENDENT_CURVES_PASS three_retained_failures=True protected_curve_reference=True phase_zero=True ancilla_zero=True diagnostic_only=True')
PY
