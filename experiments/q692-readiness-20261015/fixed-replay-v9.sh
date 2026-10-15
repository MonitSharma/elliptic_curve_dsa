#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > fixed-replay-v9.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/fixed-replay-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > fixed-replay-v9-preflight.json
test "$(cat generate-v9.exit)" = 0
test -s stream-v9.sha256
python3 prepare-fixed-replay-v9.py /home/hclau/ecdsa_research/overnight-20261014/qubits/base "$ROOT/fixed-input-replay-v9-crate"
export CARGO_TARGET_DIR="$ROOT/fixed-input-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path fixed-input-replay-v9-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path fixed-input-replay-v9-crate/Cargo.toml -- "$ROOT/stream-v9.bin" "$ROOT/failed-v6-packet-r2.json" "$ROOT/fixed-input-v9-replay.json" > fixed-input-v9-replay.log 2>&1
python3 - <<'PY'
from pathlib import Path
import json
p=Path('/home/hclau/ecdsa_research/q692_readiness_20261015/fixed-input-v9-replay.json')
r=json.loads(p.read_text(encoding='utf8'))
assert r['value_mismatch_lanes']==0,r['value_mismatch_lanes']
assert int(r['phase_word'],16)==0,r['phase_word']
assert r['ancilla_garbage']==[],r['ancilla_garbage']
print('FIXED_FULL_POINT_PASS 64_lanes three_previously_failed_curve_inputs phase_zero=True ancilla_zero=True diagnostic_only=True')
PY
