#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/reset-projection-comparators.pid
trap 'echo $? > evidence/reset-projection-comparators.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/reset-projection-comparators.resources
cp ../prefilter-macro-20261016/comparator-proof-spans-v2.tsv evidence/comparator-proof-spans-v2.tsv
sha256sum tool/target/release/reset_projection_external tool/src/reset_projection_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/comparator-proof-spans-v2.tsv ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-comparators-before.sha256
prlimit --as=17179869184 -- tool/target/release/reset_projection_external ../product-exact-20261015/tip/ops.bin evidence/reset-projection-comparators 10000 evidence/comparator-proof-spans-v2.tsv > evidence/reset-projection-comparators.report.log 2> evidence/reset-projection-comparators.progress.log || exit $?
sha256sum tool/target/release/reset_projection_external tool/src/reset_projection_external_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/comparator-proof-spans-v2.tsv ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-comparators-after.sha256
cmp evidence/reset-projection-comparators-before.sha256 evidence/reset-projection-comparators-after.sha256 || exit $?
