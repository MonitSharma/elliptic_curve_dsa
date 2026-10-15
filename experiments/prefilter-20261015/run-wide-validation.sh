#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/wide-validation.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/wide-validation.exit' EXIT
export RAYON_NUM_THREADS=1 CARGO_BUILD_JOBS=1
free -m > evidence/wide-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -50 >> evidence/wide-validation.resources
gcc -O3 -march=native -fPIC -shared simd8wide.c -o libsimd8wide.so || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin wide_verify --bin bucket_fast_wide_screen > evidence/wide.build.log 2>&1 || exit $?
tool/target/release/wide_verify /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/wide-tip.log 2> evidence/wide-tip.err || exit $?
tool/target/release/wide_verify /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/wide-product.log 2> evidence/wide-product.err || exit $?
tool/target/release/bucket_fast_wide_screen /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin 1 128 2 evidence/wide-product-screen-128.jsonl model-source 128 > evidence/wide-product-screen-128.log 2> evidence/wide-product-screen-128.err || exit $?
sha256sum simd8wide.c simd8wide.h libsimd8wide.so tool/src/fast_sim_wide.rs tool/src/simd_screen_ffi_wide.rs tool/src/wide_verify_body.rs tool/target/release/wide_verify tool/target/release/bucket_fast_wide_screen /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/wide.sha256
exit 0
