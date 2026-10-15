#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/global-anf-mask-trace.pid
trap 'echo $? > evidence/global-anf-mask-trace.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
printf '%s  %s\n' 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin | sha256sum --check || exit $?
free -m > evidence/global-anf-mask-trace.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/global-anf-mask-trace.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin global_rng_anf_mask_trace -- --nocapture > evidence/global-anf-mask-trace.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin global_rng_anf_mask_trace > evidence/global-anf-mask-trace.build.log 2>&1 || exit $?
sha256sum tool/target/release/global_rng_anf_mask_trace tool/src/global_rng_anf_mask_trace_body.rs evidence/global-anf-shadow-bound-tip32.json tool/src/mask_program_trace.rs opaque-tail-certified-v1-proof-spans.tsv tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-mask-trace-before.sha256
prlimit --as=34359738368 -- tool/target/release/global_rng_anf_mask_trace /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json > evidence/global-anf-mask-trace-tip32.json 2> evidence/global-anf-mask-trace-tip32.log || exit $?
sha256sum tool/target/release/global_rng_anf_mask_trace tool/src/global_rng_anf_mask_trace_body.rs evidence/global-anf-shadow-bound-tip32.json tool/src/mask_program_trace.rs opaque-tail-certified-v1-proof-spans.tsv tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-mask-trace-after.sha256
cmp evidence/global-anf-mask-trace-before.sha256 evidence/global-anf-mask-trace-after.sha256 || exit $?
sha256sum evidence/mr-mask-tip-v3.bin evidence/mr-mask-tip-v3.json evidence/mr-mask-tip-v3.audit-input-u64le.bin evidence/mr-mask-tip-v3.audit-known-u64le.bin > evidence/mr-mask-tip-v3.sha256
