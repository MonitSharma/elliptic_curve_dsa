#!/usr/bin/env bash
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/stream-meta-probe.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/stream-meta-probe.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_TARGET_DIR="$root/stream-resource-meta/target"
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/stream-meta-probe-preflight.json
python3 qubit-create-stream-meta.py base stream-resource-meta
cargo +1.93.0 build --release --offline --manifest-path stream-resource-meta/Cargo.toml
"$CARGO_TARGET_DIR/release/qubit_stream_resource_meta" > evidence/sizeof-op-probe.json
cat evidence/sizeof-op-probe.json
sha256sum stream-resource-meta/src/main.rs stream-resource-meta/Cargo.toml stream-resource-meta/Cargo.lock "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta"
date -u
