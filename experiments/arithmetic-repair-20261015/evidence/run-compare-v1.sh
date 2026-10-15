#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/compare.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/compare.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/fixed-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/compare-preflight.json"
python3 - <<'PY'
from pathlib import Path
root=Path('/home/hclau/ecdsa_research/arithmetic-repair-20261015')
old=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-replay/src/main.rs')
dest=root/'fixed-replay/src/bin'
dest.mkdir(exist_ok=True)
(dest/'compare_raw.rs').write_text(old.read_text().split('fn main() {')[0]+(root/'compare_raw.rs').read_text())
PY
cd "$root/fixed-replay"
cargo build --release --locked --offline --bin compare_raw > "$root/compare-build.log" 2>&1
sha256sum src/bin/compare_raw.rs "$CARGO_TARGET_DIR/release/compare_raw" > "$root/compare-source.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/compare_raw" > "$root/compare.log" 2>&1
sha256sum "$root/compare.log" > "$root/compare-log.sha256"
