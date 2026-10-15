#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/reset-projection-top1-complete.pid
trap 'echo $? > evidence/reset-projection-top1-complete.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/reset-projection-top1-complete.resources
cp ../prefilter-macro-20261016/complete-top1-proof-spans.tsv evidence/complete-top1-proof-spans.tsv
sha256sum tool/target/release/reset_projection_external tool/src/reset_projection_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/complete-top1-proof-spans.tsv ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-top1-complete-before.sha256
prlimit --as=17179869184 -- tool/target/release/reset_projection_external ../product-exact-20261015/tip/ops.bin evidence/reset-projection-top1-complete 10000 evidence/complete-top1-proof-spans.tsv > evidence/reset-projection-top1-complete.report.log 2> evidence/reset-projection-top1-complete.progress.log || exit $?
sha256sum tool/target/release/reset_projection_external tool/src/reset_projection_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/complete-top1-proof-spans.tsv ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-top1-complete-after.sha256
cmp evidence/reset-projection-top1-complete-before.sha256 evidence/reset-projection-top1-complete-after.sha256 || exit $?
