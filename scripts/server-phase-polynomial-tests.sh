#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/${1:-coordinator-phase-polynomial}"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
python3 "$root/prepare-phase-polynomial-tests.py" /home/hclau/ecdsa_research/product "$evidence/crate"
cd "$evidence/crate"
sha256sum "$root/phase_polynomial.rs" "$root/prepare-phase-polynomial-tests.py" "$root/server-phase-polynomial-tests.sh" src/*.rs Cargo.toml > "$evidence/source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/source.sha256"
/usr/bin/time -v cargo test --release --locked --offline -- --nocapture --test-threads=1
