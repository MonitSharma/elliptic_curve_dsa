#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/quantum-borrow-family-20261016
test "$(cat fresh-paired.exit)" = 0 || exit 1
test "$(cat native-verification.exit)" = 0 || exit 1
test "$(cat quantum-proofs.exit)" = 0 || exit 1
echo $$ >mapped-diagnostic.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/seam-phase-repair-20261016/tool/target
mkdir mapped-diagnostic
{ hostname; date -Is; free -h; ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >mapped-diagnostic/preflight.log
python3 prepare-mapped-diagnostic.py >mapped-diagnostic/prepare.log 2>&1
status=$?; echo $status >mapped-diagnostic/prepare.exit; [ "$status" = 0 ] || exit "$status"
cargo test --release --offline --manifest-path proof-tool/Cargo.toml --bin mapped_census -- --test-threads=1 >mapped-diagnostic/tests.log 2>&1
status=$?; echo $status >mapped-diagnostic/tests.exit; [ "$status" = 0 ] || exit "$status"
cargo build --release --offline --manifest-path proof-tool/Cargo.toml --bin mapped_census >mapped-diagnostic/build.log 2>&1
status=$?; echo $status >mapped-diagnostic/build.exit; [ "$status" = 0 ] || exit "$status"
echo '12840968ed58bb2063128d133a8f493bce3ed90256ee3b03bb5dcdc3f40dc30e  candidate/ops.bin' | sha256sum -c - >mapped-diagnostic/stream-check.log 2>&1
status=$?; echo $status >mapped-diagnostic/stream-check.exit; [ "$status" = 0 ] || exit "$status"
cp fresh-paired/input-label.txt mapped-diagnostic/input-label.txt
label=$(cat fresh-paired/input-label.txt)
"$CARGO_TARGET_DIR/release/mapped_census" candidate/ops.bin "$label" 0 4096 3 mapped-diagnostic/candidate.jsonl >mapped-diagnostic/candidate.log 2>&1
status=$?; echo $status >mapped-diagnostic/candidate.exit; echo $status >mapped-diagnostic.exit; [ "$status" = 0 ] || exit "$status"
python3 summarize-mapped.py >mapped-diagnostic/summary.log 2>&1
status=$?; echo $status >mapped-diagnostic/summary.exit; exit "$status"
