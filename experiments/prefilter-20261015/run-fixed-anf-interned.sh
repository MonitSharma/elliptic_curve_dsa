#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/fixed-anf-interned.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/fixed-anf-interned.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/fixed-anf-interned.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/fixed-anf-interned.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin fixed_rng_anf_interned -- --nocapture > evidence/fixed-anf-interned.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin fixed_rng_anf_interned > evidence/fixed-anf-interned.build.log 2>&1 || exit $?
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
tool/target/release/fixed_rng_anf_interned "$OPS" packets/audit.tsv 32 > evidence/fixed-anf-interned32.json 2> evidence/fixed-anf-interned32.log || exit $?
sha256sum tool/target/release/fixed_rng_anf_interned tool/src/fixed_rng_anf_interned.rs tool/src/fixed_rng_anf_interned_body.rs > evidence/fixed-anf-interned.sha256
exit 0
