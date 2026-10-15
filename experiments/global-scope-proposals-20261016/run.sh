#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/global-scope-proposals-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
ulimit -c 0
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
python3 -c 'import json; r=json.load(open("preflight.json")); assert r["hostname"]=="LHC-104-070" and r["memory"]["MemAvailable_bytes"]>=116*1024**3'
python3 prepare.py > prepare.log 2>&1
. /home/hclau/.cargo/env
cargo test --manifest-path tool/Cargo.toml --release --locked --offline global_tag_tests -- --nocapture > tests.log 2>&1
cargo build --manifest-path tool/Cargo.toml --release --locked --offline > build.log 2>&1
python3 case.py original4b
python3 case.py product95
