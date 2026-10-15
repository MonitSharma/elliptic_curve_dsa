#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/bucket-validation.exit' EXIT
export RAYON_NUM_THREADS=1 CARGO_BUILD_JOBS=1
free -m > evidence/bucket-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/bucket-validation.resources
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin bucket_screen > evidence/bucket-screen.build.log 2>&1 || exit $?
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
tool/target/release/bucket_screen "$OPS" 1 128 2 evidence/bucket-128.jsonl model-source 128 > evidence/bucket-128.log 2> evidence/bucket-128.err || exit $?
tool/target/release/bucket_screen "$OPS" 1 1024 2 evidence/bucket-1024.jsonl model-source 128 > evidence/bucket-1024.log 2> evidence/bucket-1024.err || exit $?
tool/target/release/advisory_screen "$OPS" 1 1024 2 evidence/advisory-1024.jsonl model-source > evidence/advisory-1024.log 2> evidence/advisory-1024.err || exit $?
tool/target/release/bucket_screen "$OPS" 1046072871506 9 2 evidence/bucket-positive9.jsonl model-source 128 > evidence/bucket-positive9.log 2> evidence/bucket-positive9.err || exit $?
sha256sum tool/target/release/bucket_screen tool/src/bucket_screen_body.rs tool/src/simd_screen_ffi.rs tool/src/rail_advisory.rs > evidence/bucket.sha256
exit 0
