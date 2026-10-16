#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/scan.pid
trap 'echo $? > a29-mask-v1/scan.exit' EXIT
ulimit -c 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-mask-v1/scan.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> a29-mask-v1/scan.resources
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/reset_projection_all_scopes_scan ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/reset-all-scopes 100000 > a29-mask-v1/scan.stdout 2> a29-mask-v1/scan.log
