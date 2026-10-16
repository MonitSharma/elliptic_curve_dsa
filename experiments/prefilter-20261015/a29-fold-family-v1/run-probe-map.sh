#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-fold-family-v1/run.pid
trap 'echo $? > a29-fold-family-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-fold-family-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-fold-family-v1/run.resources
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_whole_zero_probe > a29-fold-family-v1/build.log 2>&1 || exit $?
timeout 60 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_whole_zero_probe ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-relations-v2/report.json > a29-fold-family-v1/probe.json 2> a29-fold-family-v1/probe.log || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-fold-family-v1/hints.json a29-mask-v2/candidates-v3.json > a29-fold-family-v1/candidates.json 2> a29-fold-family-v1/map.log
