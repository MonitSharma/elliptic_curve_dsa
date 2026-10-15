#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >primitive-bdd.pid
while [ ! -f source-v2-raw-verification.exit ];do sleep 5;done
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-primitive-bdd.log
python3 prepare-primitive-bdd.py >prepare-primitive-bdd.log 2>&1
status=$?;echo $status >prepare-primitive-bdd.exit;[ "$status" = 0 ] || exit "$status"
cargo test --release --manifest-path tool/Cargo.toml --bin phase_primitive -- --test-threads=1 >primitive-bdd-tests.log 2>&1
status=$?;echo $status >primitive-bdd-tests.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --manifest-path tool/Cargo.toml --bin phase_primitive >build-primitive-bdd.log 2>&1
status=$?;echo $status >build-primitive-bdd.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/phase_primitive ../product-exact-20261015/tip/ops.bin 689514 >primitive-bdd-689514.json 2>primitive-bdd-689514.log
status=$?;echo $status >primitive-bdd-689514.exit;exit "$status"
