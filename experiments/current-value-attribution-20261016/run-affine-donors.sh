#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > affine-donor.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >affine-donor-preflight.log
python3 prepare-affine-donors.py >affine-donor-prepare.log 2>&1
code=$?;echo "$code" >affine-donor-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --offline --manifest-path tool/Cargo.toml --bin affine_loan_donors >affine-donor-build.log 2>&1
code=$?;echo "$code" >affine-donor-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target-tool/release/affine_loan_donors >affine-donor.jsonl 2>affine-donor.log
code=$?;echo "$code" >affine-donor.exit
exit "$code"
