#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/capacity-validation.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/capacity-validation.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/capacity-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/capacity-validation.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin advisory_screen compact_capacity_tests -- --nocapture > evidence/capacity16.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin wide_verify compact_capacity_tests -- --nocapture > evidence/capacity32.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin wide_verify --bin bucket_fast_wide_screen --bin bucket_fast_screen > evidence/capacity.build.log 2>&1 || exit $?
tool/target/release/wide_verify /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/capacity-product-paired.log 2> evidence/capacity-product-paired.err || exit $?
tool/target/release/bucket_fast_wide_screen /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin 1046072871510 1 1 evidence/capacity-wide-positive.jsonl model-source 128 > evidence/capacity-wide-positive.log 2> evidence/capacity-wide-positive.err || exit $?
exit 0
