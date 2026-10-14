#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014
evidence=${1:-coordinator-wire-zero}
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 16777216
date -u
hostname
python3 ../server-preflight.py
git -C ../product rev-parse HEAD
sha256sum prepare-wire-zero-audit.py server-wire-zero-audit.sh
python3 prepare-wire-zero-audit.py ../product "$evidence/crate"
. /home/hclau/.cargo/env
(cd "$evidence/crate" && cargo generate-lockfile --offline)
/usr/bin/time -v cargo build --release --locked --offline --manifest-path "$evidence/crate/Cargo.toml"
sha256sum "$evidence/crate/Cargo.lock" "$evidence/crate/src/"*.rs
/usr/bin/time -v "$evidence/crate/target/release/wire_zero_audit" ../product/ops.bin 1444991
