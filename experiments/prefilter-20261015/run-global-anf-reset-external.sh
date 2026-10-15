#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/global-anf-reset-external.pid
trap 'echo $? > evidence/global-anf-reset-external.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/global-anf-reset-external.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/global-anf-reset-external.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin global_rng_anf_reset_external -- --nocapture > evidence/global-anf-reset-external.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin global_rng_anf_reset_external > evidence/global-anf-reset-external.build.log 2>&1 || exit $?
sha256sum tool/target/release/global_rng_anf_reset_external tool/src/global_rng_anf_reset_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-reset-external-before.sha256
prlimit --as=34359738368 -- tool/target/release/global_rng_anf_reset_external /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json > evidence/global-anf-reset-external-tip32.json 2> evidence/global-anf-reset-external-tip32.log || exit $?
sha256sum tool/target/release/global_rng_anf_reset_external tool/src/global_rng_anf_reset_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/global-anf-reset-external-after.sha256
cmp evidence/global-anf-reset-external-before.sha256 evidence/global-anf-reset-external-after.sha256 || exit $?
