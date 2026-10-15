#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/shadow-value-zeros.pid
trap 'echo $? > evidence/shadow-value-zeros.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/shadow-value-zeros.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/shadow-value-zeros.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin shadow_value_zeros -- --nocapture > evidence/shadow-value-zeros.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin shadow_value_zeros > evidence/shadow-value-zeros.build.log 2>&1 || exit $?
sha256sum tool/target/release/shadow_value_zeros tool/src/shadow_value_contract_zeros.rs tool/src/global_rng_anf_retained_masks.rs tool/src/input_anf_dag16.rs ../product-exact-20261015/tip/ops.bin > evidence/shadow-value-zeros-before.sha256
prlimit --as=8589934592 -- tool/target/release/shadow_value_zeros ../product-exact-20261015/tip/ops.bin evidence/prefix-state-carry-tip32.json > evidence/shadow-value-zeros-carry.json 2> evidence/shadow-value-zeros-carry.log || exit $?
sha256sum tool/target/release/shadow_value_zeros tool/src/shadow_value_contract_zeros.rs tool/src/global_rng_anf_retained_masks.rs tool/src/input_anf_dag16.rs ../product-exact-20261015/tip/ops.bin > evidence/shadow-value-zeros-after.sha256
cmp evidence/shadow-value-zeros-before.sha256 evidence/shadow-value-zeros-after.sha256
