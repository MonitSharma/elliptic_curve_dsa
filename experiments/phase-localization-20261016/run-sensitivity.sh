#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >sensitivity.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-sensitivity.log
python3 prepare-sensitivity.py >prepare-sensitivity.log 2>&1
status=$?;echo $status >prepare-sensitivity.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --manifest-path tool/Cargo.toml >build-sensitivity-export.log 2>&1
status=$?;echo $status >build-sensitivity-export.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/value_prefilter ../product-exact-20261015/tip/ops.bin witnesses.tsv marks.txt >trace-export.jsonl 2>trace-export.log
status=$?;echo $status >trace-export.exit;[ "$status" = 0 ] || exit "$status"
gcc -O3 -march=native -std=c11 sensitivity.c simd8.c -o sensitivity >build-sensitivity.log 2>&1
status=$?;echo $status >build-sensitivity.exit;[ "$status" = 0 ] || exit "$status"
for lane in 0 1 2 3;do
 for base in 0 1;do
  (./sensitivity "$lane" "$base" >"sensitivity-$lane-$base.jsonl" 2>"sensitivity-$lane-$base.log";echo $? >"sensitivity-$lane-$base.exit") &
 done
done
wait
echo 0 >sensitivity-wrapper.exit
