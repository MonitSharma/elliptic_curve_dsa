#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-linear-witness-native"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
python3 "$root/prepare-linear-witness-candidate.py" /home/hclau/ecdsa_research/product "$evidence"
cd "$evidence/crate"
sha256sum "$root/prepare-linear-witness-candidate.py" "$root/prepare-linear-span-audit.py" "$root/prepare-linear-pair-audit.py" "$root/prepare-wire-zero-audit.py" "$root/server-linear-witness-native.sh" src/*.rs Cargo.toml "$evidence/candidate-source/point_add/"*.rs > "$evidence/source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/source.sha256"
cargo test --release --locked --offline -- --nocapture --test-threads=1
cargo build --release --locked --offline
sha256sum target/release/linear_witness_native >> "$evidence/source.sha256"
/usr/bin/time -v target/release/linear_witness_native /home/hclau/ecdsa_research/product/ops.bin
