#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-edited-folds-v1/run.pid
trap 'echo $? > a29-edited-folds-v1/run.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-edited-folds-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-edited-folds-v1/run.resources
printf '%s  %s\n' ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69 ../prefilter-macro-20261016/raw-builder.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../prefilter-macro-20261016/raw-builder.bin ../product-exact-20261015/tip/ops.bin a29-edited-folds-v1/raw-hints.json a29-edited-folds-v1/raw-to-original-guide.json > a29-edited-folds-v1/original-candidates.json 2> a29-edited-folds-v1/original-map.log || exit $?
python3 a29-edited-folds-v1/prepare-second.py || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-edited-folds-v1/original-final-hints.json a29-mask-v2/candidates-v3.json > a29-edited-folds-v1/a29-candidates.json 2> a29-edited-folds-v1/a29-map.log
