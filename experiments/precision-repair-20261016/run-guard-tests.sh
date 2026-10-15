#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" RAYON_NUM_THREADS=1
{ date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -12; } > preflight-guards.log
deps=candidate-one-bit-top1/target/release/deps
lib=$(find "$deps" -maxdepth 1 -name 'libquantum_ecc-*.rlib' | head -1)
rustup run 1.93.0 rustc --edition=2021 --test -O guard-tests.rs -L "dependency=$deps" --extern "quantum_ecc=$lib" -o guard-tests > build-guard-tests.log 2>&1
code=$?;echo "$code" > build-guard-tests.exit
if [ "$code" -ne 0 ];then exit "$code";fi
./guard-tests --nocapture > guard-tests.log 2>&1
code=$?;echo "$code" > guard-tests.exit
exit "$code"
