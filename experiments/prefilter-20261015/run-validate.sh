#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > evidence/validate.exit' EXIT
export RAYON_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 62914560
date -Is > evidence/validate.start
hostname > evidence/validate.hostname
uptime > evidence/validate.resources
free -g >> evidence/validate.resources
ps -eo pid,comm,pcpu,pmem,args --sort=-pcpu | head -20 >> evidence/validate.resources
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
sha256sum "$OPS" > evidence/tip-stream.sha256
nohup /usr/bin/time -v tool/target/release/fast_screen "$OPS" 1 128 8 evidence/fast-screen-1-128.jsonl > evidence/fast-screen-1-128.out 2> evidence/fast-screen-1-128.err &
fast_pid=$!
echo "$fast_pid" > evidence/fast-screen.pid
nohup /usr/bin/time -v /home/hclau/ecdsa_research/nonce-screen-20261015/screen/target/release/nonce_screen "$OPS" 1 128 8 evidence/reference-screen-1-128.jsonl > evidence/reference-screen-1-128.out 2> evidence/reference-screen-1-128.err &
ref_pid=$!
echo "$ref_pid" > evidence/reference-screen.pid
wait "$fast_pid"
wait "$ref_pid"
python3 compare.py
date -Is > evidence/validate.end
