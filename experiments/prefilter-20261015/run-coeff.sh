#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/rng-coeff.exit' EXIT
echo $$ > evidence/rng-coeff.pid
ulimit -v 62914560
export PATH=/home/hclau/.cargo/bin:$PATH CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
uptime > evidence/rng-coeff.resources
free -g >> evidence/rng-coeff.resources
cargo test --release --locked --offline --manifest-path tool/Cargo.toml --bin rng_coeff > evidence/rng-coeff.tests.log 2>&1
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin rng_coeff > evidence/rng-coeff.build.log 2>&1
/usr/bin/time -v tool/target/release/rng_coeff /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin 32 > evidence/rng-coeff.json 2> evidence/rng-coeff.log
