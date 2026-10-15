#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > fixed-packet-v9.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/fixed-packet-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > fixed-packet-v9-preflight.json
test "$(cat generate-v9.exit)" = 0
test "$(cat fixed-replay-v9.exit)" = 0
# Resolve the newly retained independent failure cases before spending another
# hour on the old packet. A failing independent curve test stops promotion.
bash independent-curves-v9.sh
python3 prepare-fixed-packet-replay.py /home/hclau/ecdsa_research/overnight-20261014/qubits/base "$ROOT/fixed-packet-v9-crate"
export CARGO_TARGET_DIR="$ROOT/fixed-packet-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path fixed-packet-v9-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path fixed-packet-v9-crate/Cargo.toml -- "$ROOT/stream-v9.bin" "$ROOT/failed-v6-packet-r2.json" "$ROOT/fixed-packet-v9-result.json" > fixed-packet-v9-proof.log 2>&1
