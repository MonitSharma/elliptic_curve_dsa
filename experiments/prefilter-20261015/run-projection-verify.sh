#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/projection-verify.pid
trap 'echo $? > evidence/projection-verify.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/projection-verify.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/projection-verify.resources
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin projection_verify > evidence/projection-verify.build.log 2>&1 || exit $?
sha256sum tool/target/release/projection_verify tool/src/projection_verify_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-verify-before.sha256
for fixture in all-failing-tip sensitivity-structured sensitivity-arbitrary; do
 prlimit --as=17179869184 -- tool/target/release/projection_verify ../product-exact-20261015/tip/ops.bin "packets/$fixture.tsv" 32 evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json > "evidence/projection-verify-$fixture.json" 2> "evidence/projection-verify-$fixture.log" || exit $?
done
sha256sum tool/target/release/projection_verify tool/src/projection_verify_body.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json ../product-exact-20261015/tip/ops.bin > evidence/projection-verify-after.sha256
cmp evidence/projection-verify-before.sha256 evidence/projection-verify-after.sha256 || exit $?
