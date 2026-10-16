#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/candidate67-static-abi.pid
trap 'echo $? > evidence/candidate67-static-abi.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > evidence/candidate67-static-abi.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> evidence/candidate67-static-abi.resources
printf '%s  %s\n' 268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin stream_abi_audit > evidence/candidate67-static-abi.build.log 2>&1 || exit $?
sha256sum tool/src/bin/stream_abi_audit.rs tool/target/release/stream_abi_audit ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin ../product-exact-20261015/tip/ops.bin > evidence/candidate67-static-abi-before.sha256
prlimit --as=8589934592 -- tool/target/release/stream_abi_audit ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin > evidence/candidate67-static-abi.json 2> evidence/candidate67-static-abi.log || exit $?
sha256sum tool/src/bin/stream_abi_audit.rs tool/target/release/stream_abi_audit ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin ../product-exact-20261015/tip/ops.bin > evidence/candidate67-static-abi-after.sha256
cmp evidence/candidate67-static-abi-before.sha256 evidence/candidate67-static-abi-after.sha256
