#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/map.pid
trap 'echo $? > a29-mask-v1/map.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-mask-v1/map.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> a29-mask-v1/map.resources
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_contract_map > a29-mask-v1/map.build.log 2>&1 || exit $?
timeout 300 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/old-boundary-hints.json > a29-mask-v1/candidates.json 2> a29-mask-v1/map.log
