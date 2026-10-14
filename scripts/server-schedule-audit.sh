#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/${1:-coordinator-schedule}"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
git -C "$root/qubits/base" rev-parse HEAD
git -C "$root/qubits/base" status --short
python3 "$root/prepare-schedule-audit.py" "$root/qubits/base" "$evidence/crate"
cd "$evidence/crate"
sha256sum "$root/prepare-schedule-audit.py" "$root/server-schedule-audit.sh" src/main.rs Cargo.toml > "$evidence/source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/source.sha256"
cargo build --release --locked --offline
sha256sum target/release/public_schedule_audit "$root/qubits/evidence/compact-packet.tsv" >> "$evidence/source.sha256"
/usr/bin/time -v target/release/public_schedule_audit "$root/qubits/evidence/compact-packet.tsv"
