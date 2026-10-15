#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/global-scope-proposals-20261016
cd "$ROOT"
echo $$ > audit.pid
trap 'rc=$?; echo "$rc" > "$ROOT/audit.exit"' EXIT
export CARGO_BUILD_JOBS=1 OMP_NUM_THREADS=1
python3 audit-prepare.py > audit-prepare.log 2>&1
. /home/hclau/.cargo/env
cargo build --manifest-path audit-tool/Cargo.toml --release --offline > audit-build.log 2>&1
prlimit --as=2147483648 -- audit-tool/target/release/scope_proposal_audit /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin original4b.log > original4b-BOUND-AUDIT.json 2> audit.log
