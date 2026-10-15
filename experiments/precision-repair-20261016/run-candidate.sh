#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-candidate.log
test "$(cat population.exit)" = 0 || exit 1
python3 aggregate-census.py > fold-risk-summary.log 2>&1
code=$?;echo "$code" > aggregate-census.exit
if [ "$code" -ne 0 ];then exit "$code";fi
python3 prepare-candidate.py > prepare-candidate.log 2>&1
code=$?;echo "$code" > prepare-candidate.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd candidate-one-bit-top1
cargo build --release --locked --offline --bin build_circuit > ../build-candidate.log 2>&1
code=$?;echo "$code" > ../build-candidate.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target/release/build_circuit > ../candidate.log 2>&1
code=$?;echo "$code" > ../candidate.exit
if [ "$code" -eq 0 ];then sha256sum ops.bin > ../candidate-stream.sha256;fi
exit "$code"
