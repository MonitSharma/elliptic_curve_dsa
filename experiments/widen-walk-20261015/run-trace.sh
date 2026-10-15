#!/usr/bin/env bash
# Gate-inert first-divergence trace of a widened variant's own value failures. Diagnostic; score=NONE.
set -euo pipefail
v=${1:-mid2-smooth}
base=/home/hclau/ecdsa_research/widen-walk-20261015
tv=/home/hclau/ecdsa_research/trace-value-20261015
root=$base/trace-$v
mkdir "$root"; cd "$root"; echo $$ > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
sed "s#/home/hclau/ecdsa_research/trace-value-20261015#$root#" "$tv/value_trace.rs" > value_trace.rs
cp "$tv/prepare.py" "$tv/points.py" .
python3 points.py "$base/$v/census.jsonl" fails.tsv /home/hclau/ecdsa_research/guard-sweep-20261015 > points.log
python3 prepare.py "$root" "$base/$v/src-b3" "$root/fails.tsv" "$(cut -d' ' -f1 $base/$v/stream.sha256)" > prepare.log 2>&1
cd observer-b3
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../trace.log 2>&1
sha256sum ops.bin > ../stream.sha256
if [ "$(cut -d' ' -f1 ../stream.sha256)" = "$(cut -d' ' -f1 $base/$v/stream.sha256)" ]; then echo BYTE_IDENTICAL_STREAM=true; else echo BYTE_IDENTICAL_STREAM=false; fi > ../equality.log
