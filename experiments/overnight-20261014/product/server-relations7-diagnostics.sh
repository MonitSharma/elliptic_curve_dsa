#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/relations7
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/diagnostics.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/overnight-20261014/product-scan-streams.py "$evidence/ops.bin" --out "$evidence/stream-diagnostic.json"
python3 /home/hclau/ecdsa_research/overnight-20261014/product-scan-streams.py /home/hclau/ecdsa_research/product/ops.bin --out "$evidence/baseline-stream-diagnostic.json"
python3 /home/hclau/ecdsa_research/overnight-20261014/product-create-paired-replay.py /home/hclau/ecdsa_research/product /home/hclau/ecdsa_research/overnight-20261014/product-replay
cd /home/hclau/ecdsa_research/overnight-20261014/product-replay
/usr/bin/time -v cargo build --offline --release
sha256sum src/main.rs Cargo.toml > "$evidence/diagnostic-source.sha256"
/usr/bin/time -v target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product/ops.bin "$evidence/ops.bin" independent "$evidence/independent.tsv"
/usr/bin/time -v target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product/ops.bin "$evidence/ops.bin" structured "$evidence/structured.tsv"
date -u
