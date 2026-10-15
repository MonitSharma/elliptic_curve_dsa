#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/advisory-edge-tests.exit' EXIT
export RAYON_NUM_THREADS=1 CARGO_BUILD_JOBS=1
free -m > evidence/advisory-edge-tests.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/advisory-edge-tests.resources
sha256sum tool/target/release/advisory_screen > evidence/advisory-v1-binary.sha256
cp tool/target/release/advisory_screen tool/target/release/advisory_screen-v1
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin advisory_screen acceptance_tests -- --nocapture > evidence/advisory-acceptance-tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin advisory_screen > evidence/advisory-screen-v2.build.log 2>&1 || exit $?
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
ADVISORY_NO_HIT=1 tool/target/release/advisory_screen "$OPS" 1046072871510 1 1 evidence/advisory-no-hit-positive.jsonl model-source > evidence/advisory-no-hit-positive.log 2> evidence/advisory-no-hit-positive.err || exit $?
tool/target/release/advisory_screen "$OPS" 1046072871506 9 2 evidence/advisory-lowest-positive.jsonl model-source > evidence/advisory-lowest-positive.log 2> evidence/advisory-lowest-positive.err || exit $?
sha256sum tool/target/release/advisory_screen tool/src/advisory_screen_body.rs tool/src/simd_screen_ffi.rs tool/src/rail_advisory.rs > evidence/advisory-v2.sha256
exit 0
