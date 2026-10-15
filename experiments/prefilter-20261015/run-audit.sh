#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/rng-audit.exit' EXIT
echo $$ > evidence/rng-audit.pid
ulimit -v 62914560
export PATH=/home/hclau/.cargo/bin:$PATH CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
uptime > evidence/rng-audit.resources
free -g >> evidence/rng-audit.resources
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin rng_audit > evidence/rng-audit.build.log 2>&1
/usr/bin/time -v tool/target/release/rng_audit /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/rng-audit.json 2> evidence/rng-audit.log
