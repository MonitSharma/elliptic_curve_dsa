#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/${1:-coordinator-decision-phase-tests}"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
python3 "$root/prepare-decision-phase-tests.py" "$root/qubits/base" "$evidence/crate"
cd "$evidence/crate"
export CARGO_TARGET_DIR="$evidence/target"
sha256sum "$root/phase_decision_diagram.rs" "$root/prepare-decision-phase-tests.py" "$root/server-decision-phase-tests.sh" src/*.rs Cargo.toml > "$evidence/source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/source.sha256"
/usr/bin/time -v cargo test --release --locked --offline -- --nocapture --test-threads=1
