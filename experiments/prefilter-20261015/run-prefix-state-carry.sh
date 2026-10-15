#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/prefix-state-carry.pid
trap 'echo $? > evidence/prefix-state-carry.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/prefix-state-carry.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/prefix-state-carry.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin prefix_state -- --nocapture > evidence/prefix-state-carry.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin prefix_state > evidence/prefix-state-carry.build.log 2>&1 || exit $?
sha256sum tool/target/release/prefix_state tool/src/prefix_state_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/prefix-state-carry-before.sha256
prlimit --as=34359738368 -- tool/target/release/prefix_state /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json > evidence/prefix-state-carry-tip32.json 2> evidence/prefix-state-carry-tip32.log || exit $?
sha256sum tool/target/release/prefix_state tool/src/prefix_state_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/prefix-state-carry-after.sha256
cmp evidence/prefix-state-carry-before.sha256 evidence/prefix-state-carry-after.sha256 || exit $?
