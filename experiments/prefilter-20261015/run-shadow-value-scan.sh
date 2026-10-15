#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/shadow-value-scan.pid
trap 'echo $? > evidence/shadow-value-scan.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/shadow-value-scan.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/shadow-value-scan.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin shadow_value_scan -- --nocapture > evidence/shadow-value-scan.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin shadow_value_scan > evidence/shadow-value-scan.build.log 2>&1 || exit $?
sha256sum tool/target/release/shadow_value_scan tool/src/shadow_value_contract.rs tool/src/global_rng_anf_retained_masks.rs tool/src/input_anf_dag16.rs ../product-exact-20261015/tip/ops.bin > evidence/shadow-value-scan-before.sha256
prlimit --as=8589934592 -- tool/target/release/shadow_value_scan ../product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/prefilter-macro-20261016/additional/carry-helper-proof-spans.tsv > evidence/shadow-value-carry.json 2> evidence/shadow-value-carry.log || exit $?
sha256sum tool/target/release/shadow_value_scan tool/src/shadow_value_contract.rs tool/src/global_rng_anf_retained_masks.rs tool/src/input_anf_dag16.rs ../product-exact-20261015/tip/ops.bin > evidence/shadow-value-scan-after.sha256
cmp evidence/shadow-value-scan-before.sha256 evidence/shadow-value-scan-after.sha256
