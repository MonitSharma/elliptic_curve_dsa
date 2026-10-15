#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/fixed-anf.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/fixed-anf.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/fixed-anf.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/fixed-anf.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin fixed_rng_anf fixed_anf_tests -- --nocapture > evidence/fixed-anf.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin fixed_rng_anf > evidence/fixed-anf.build.log 2>&1 || exit $?
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
tool/target/release/fixed_rng_anf "$OPS" packets/audit.tsv 32 > evidence/fixed-anf32.json 2> evidence/fixed-anf32.log || exit $?
tool/target/release/fixed_rng_anf "$OPS" packets/audit.tsv 128 > evidence/fixed-anf128.json 2> evidence/fixed-anf128.log || exit $?
sha256sum tool/target/release/fixed_rng_anf tool/src/fixed_rng_anf.rs tool/src/fixed_rng_anf_body.rs > evidence/fixed-anf.sha256
exit 0
