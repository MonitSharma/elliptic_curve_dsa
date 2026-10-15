#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/proof.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/proof.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/fixed-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/proof-preflight.json"
python3 - <<'PY'
from pathlib import Path
root=Path('/home/hclau/ecdsa_research/arithmetic-repair-20261015')
old=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-replay/src/main.rs')
(root/'fixed-replay/src/proof_kernel.rs').write_bytes((root/'proof_kernel.rs').read_bytes())
(root/'fixed-replay/src/bin/local_proof.rs').write_text(old.read_text().split('fn main() {')[0]+(root/'local_proof.rs').read_text())
PY
cd "$root/fixed-replay"
cargo build --release --locked --offline --bin local_proof > "$root/proof-build.log" 2>&1
sha256sum src/bin/local_proof.rs src/proof_kernel.rs "$CARGO_TARGET_DIR/release/local_proof" > "$root/proof-source.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/local_proof" > "$root/proof.log" 2>&1
sha256sum "$root/proof.log" > "$root/proof-log.sha256"
