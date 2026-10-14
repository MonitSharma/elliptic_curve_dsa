#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-stream-packet-v1"
mkdir -p "$evidence"
echo "$$" > "$evidence/run.pid"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
sha256sum "$root/prepare-stream-packet.py" "$root/server-stream-packet.sh" > "$evidence/helper-source.sha256"
python3 "$root/prepare-stream-packet.py" "$root/qubits/harness-n275-v2" "$evidence/crate"
cd "$evidence/crate"
. /home/hclau/.cargo/env
export CARGO_TARGET_DIR="$evidence/target"
cargo generate-lockfile --offline
cargo build --locked --offline --release
sha256sum "$evidence/target/release/fixed_stream_packet" > "$evidence/native.sha256"
/usr/bin/time -v "$evidence/target/release/fixed_stream_packet" check-small /home/hclau/ecdsa_research/product/ops.bin "$evidence/unwritten-small.tsv"
/usr/bin/time -v timeout 1800 "$evidence/target/release/fixed_stream_packet" export "$root/qubits/evidence/n275-v2-ops.bin" "$evidence/n275-v2-official-packet.tsv"
sha256sum "$evidence/n275-v2-official-packet.tsv" "$evidence/n275-v2-official-packet.tsv.batch37-rng-prefix.bin"
date -u
