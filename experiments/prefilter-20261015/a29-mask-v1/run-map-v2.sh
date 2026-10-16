#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/map-v2.pid
trap 'echo $? > a29-mask-v1/map-v2.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_contract_map_v2 --bin a29_rng_mask > a29-mask-v1/build-v2.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v2 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/old-boundary-hints.json a29-mask-v1/candidates.json > a29-mask-v1/candidates-v2.json 2> a29-mask-v1/map-v2.log
