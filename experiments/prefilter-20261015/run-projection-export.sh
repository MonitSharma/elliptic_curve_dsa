#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/projection-export.pid
trap 'echo $? > evidence/projection-export.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/projection-export.resources
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin projection_export > evidence/projection-export.build.log 2>&1 || exit $?
sha256sum tool/target/release/projection_export tool/src/projection_export_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs tool/src/fast_sim_wide.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-export-before.sha256
prlimit --as=17179869184 -- tool/target/release/projection_export ../product-exact-20261015/tip/ops.bin evidence/certified-reduced-tip 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json > evidence/projection-export.log 2>&1 || exit $?
sha256sum evidence/certified-reduced-tip.ops.bin evidence/certified-reduced-tip.compact16.bin evidence/certified-reduced-tip.json > evidence/certified-reduced-tip.sha256
sha256sum tool/target/release/projection_export tool/src/projection_export_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs tool/src/fast_sim_wide.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-export-after.sha256
cmp evidence/projection-export-before.sha256 evidence/projection-export-after.sha256 || exit $?
