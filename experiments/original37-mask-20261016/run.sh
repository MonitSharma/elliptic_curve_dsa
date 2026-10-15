#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/original37-mask-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
ulimit -c 0
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
python3 prepare.py > prepare.log 2>&1
. /home/hclau/.cargo/env
cargo test --manifest-path tool/Cargo.toml --release --locked --offline --bin original37_mask -- --nocapture > tests.log 2>&1
cargo build --manifest-path tool/Cargo.toml --release --locked --offline --bin original37_mask > build.log 2>&1
INPUT=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
sha256sum "$INPUT" > input-before.sha256
grep -q '^2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ' input-before.sha256
prlimit --as=25769803776 -- tool/target/release/original37_mask "$INPUT" packets/audit.tsv 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json > global.json 2> global.log
sha256sum "$INPUT" > input-after.sha256
cmp input-before.sha256 input-after.sha256
sha256sum evidence/mr-mask-original37.bin evidence/mr-mask-original37.json evidence/mr-mask-original37.audit-input-u64le.bin evidence/mr-mask-original37.audit-known-u64le.bin > published.sha256
