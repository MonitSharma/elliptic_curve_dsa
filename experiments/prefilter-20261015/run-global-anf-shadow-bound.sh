#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/global-anf-shadow-bound.pid
trap 'echo $? > evidence/global-anf-shadow-bound.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/global-anf-shadow-bound.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/global-anf-shadow-bound.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin global_rng_anf_shadow_bound -- --nocapture > evidence/global-anf-shadow-bound.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin global_rng_anf_shadow_bound > evidence/global-anf-shadow-bound.build.log 2>&1 || exit $?
sha256sum tool/target/release/global_rng_anf_shadow_bound tool/src/global_rng_anf_shadow_bound_body.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-shadow-bound-before.sha256
prlimit --as=34359738368 -- tool/target/release/global_rng_anf_shadow_bound /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json > evidence/global-anf-shadow-bound-tip32.json 2> evidence/global-anf-shadow-bound-tip32.log || exit $?
sha256sum tool/target/release/global_rng_anf_shadow_bound tool/src/global_rng_anf_shadow_bound_body.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-shadow-bound-after.sha256
cmp evidence/global-anf-shadow-bound-before.sha256 evidence/global-anf-shadow-bound-after.sha256 || exit $?
