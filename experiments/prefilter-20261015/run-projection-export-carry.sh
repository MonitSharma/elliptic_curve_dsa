#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/projection-export-carry.pid
trap 'echo $? > evidence/projection-export-carry.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/projection-export-carry.resources
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin projection_export > evidence/projection-export-carry.build.log 2>&1 || exit $?
sha256sum tool/target/release/projection_export tool/src/projection_export_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs tool/src/fast_sim_wide.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-export-carry-before.sha256
prlimit --as=17179869184 -- tool/target/release/projection_export ../product-exact-20261015/tip/ops.bin evidence/certified-reduced-tip-carry 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json > evidence/projection-export-carry.log 2>&1 || exit $?
sha256sum evidence/certified-reduced-tip-carry.ops.bin evidence/certified-reduced-tip-carry.compact16.bin evidence/certified-reduced-tip-carry.json > evidence/certified-reduced-tip-carry.sha256
sha256sum tool/target/release/projection_export tool/src/projection_export_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs tool/src/fast_sim_wide.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-export-carry-after.sha256
cmp evidence/projection-export-carry-before.sha256 evidence/projection-export-carry-after.sha256 || exit $?
