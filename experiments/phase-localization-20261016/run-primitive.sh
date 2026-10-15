#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >primitive.pid
while [ ! -f sensitivity64-wrapper.exit ];do sleep 5;done
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-primitive.log
python3 prepare-primitive.py >prepare-primitive.log 2>&1
status=$?;echo $status >prepare-primitive.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --manifest-path tool/Cargo.toml --bin phase_primitive >build-primitive.log 2>&1
status=$?;echo $status >build-primitive.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/phase_primitive ../product-exact-20261015/tip/ops.bin 689514 >primitive-689514.json 2>primitive-689514.log
status=$?;echo $status >primitive-689514.exit;exit "$status"
