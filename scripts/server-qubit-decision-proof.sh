#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/${1:-coordinator-qubit-decision-proof}"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
sha256sum "$root/phase_decision_diagram.rs" "$root/prepare-qubit-decision-proof.py" "$root/server-qubit-decision-proof.sh" > "$evidence/launcher-source.sha256"
python3 "$root/prepare-qubit-decision-proof.py" "$root/qubits/${2:-candidate-ph-owner}" "$root/qubits/base" "$evidence/crate"
cd "$evidence/crate"
export CARGO_TARGET_DIR="$evidence/target"
sha256sum "$root/phase_decision_diagram.rs" "$root/prepare-qubit-decision-proof.py" src/*.rs Cargo.toml source/point_add/{midg,frogdrop,tests_midg_k24,mod}.rs > "$evidence/source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/source.sha256"
/usr/bin/time -v cargo test --release --locked --offline coordinator_ -- --nocapture --test-threads=1
