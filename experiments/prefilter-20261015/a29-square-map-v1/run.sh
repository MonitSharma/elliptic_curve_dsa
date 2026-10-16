#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-square-map-v1/run.pid
trap 'echo $? > a29-square-map-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-square-map-v1/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-square-map-v1/resources
python3 a29-square-map-v1/prepare-hints.py || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_square_map_v1 > a29-square-map-v1/build.log 2>&1 || exit $?
sha256sum tool/src/bin/a29_square_map_v1.rs a29-square-map-v1/hints.json ../prefilter-macro-20261016/raw-builder.bin ../product-exact-20261015/tip/ops.bin > a29-square-map-v1/before.sha256
timeout 180 prlimit --as=8589934592 -- tool/target/release/a29_square_map_v1 ../prefilter-macro-20261016/raw-builder.bin ../product-exact-20261015/tip/ops.bin a29-square-map-v1/hints.json > a29-square-map-v1/original-candidates.json 2> a29-square-map-v1/map.log || exit $?
sha256sum tool/src/bin/a29_square_map_v1.rs a29-square-map-v1/hints.json ../prefilter-macro-20261016/raw-builder.bin ../product-exact-20261015/tip/ops.bin > a29-square-map-v1/after.sha256
cmp a29-square-map-v1/before.sha256 a29-square-map-v1/after.sha256
