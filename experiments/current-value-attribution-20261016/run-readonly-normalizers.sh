#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
python3 prepare-readonly-normalizers.py >readonly-normalizers-prepare.log 2>&1
code=$?;echo "$code" >readonly-normalizers-prepare.exit;if [ "$code" -ne 0 ];then exit "$code";fi
cd ../n2-readonly-normalizers-20261016
echo $$ >query.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >preflight.log
sha256sum ../product-exact-20261015/tip/ops.bin family.json tool/src/support.rs tool/src/bin/readonly_loans.rs >before.sha256
cargo test --release --locked --offline --manifest-path tool/Cargo.toml --bin readonly_loans -- --test-threads=1 >tests.log 2>&1
code=$?;echo "$code" >tests.exit;if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin readonly_loans >build.log 2>&1
code=$?;echo "$code" >build.exit;if [ "$code" -ne 0 ];then exit "$code";fi
(ulimit -v 16777216;/usr/bin/time -v "$CARGO_TARGET_DIR/release/readonly_loans" ../product-exact-20261015/tip/ops.bin family.json) >query.jsonl 2>query.log
code=$?;echo "$code" >query.exit
sha256sum ../product-exact-20261015/tip/ops.bin family.json tool/src/support.rs tool/src/bin/readonly_loans.rs >after.sha256
cmp before.sha256 after.sha256 || exit 91
exit "$code"
