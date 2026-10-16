#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-conditional-transfer-v2/run.pid
trap 'echo $? > a29-conditional-transfer-v2/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-conditional-transfer-v2/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-conditional-transfer-v2/resources
cp ../precision-family-20261016/isolated/tick-128.old.bin ../precision-family-20261016/isolated/tick-128.new.bin ../precision-family-20261016/isolated/tick-128.interface.json a29-conditional-transfer-v2/
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_pair_fold128_full -- --nocapture > a29-conditional-transfer-v2/tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_pair_fold128_full > a29-conditional-transfer-v2/build.log 2>&1 || exit $?
files='tool/src/bin/a29_pair_fold128_full.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs a29-conditional-transfer-v2/tick-128.old.bin a29-conditional-transfer-v2/tick-128.new.bin a29-conditional-transfer-v2/tick-128.interface.json a29-conditional-transfer-v2/tick128-prefix-receipt.json'
sha256sum $files > a29-conditional-transfer-v2/before.sha256
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_pair_fold128_full a29-conditional-transfer-v2/tick-128.old.bin a29-conditional-transfer-v2/tick-128.new.bin a29-conditional-transfer-v2/tick128-prefix-receipt.json a29-conditional-transfer-v2/tick-128.interface.json > a29-conditional-transfer-v2/result.json 2> a29-conditional-transfer-v2/result.log || exit $?
sha256sum $files > a29-conditional-transfer-v2/after.sha256
cmp a29-conditional-transfer-v2/before.sha256 a29-conditional-transfer-v2/after.sha256
