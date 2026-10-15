#!/usr/bin/env bash
# Widened leapfrog walk table variants of the wide circuit: build, generate, census. Diagnostic; score=NONE.
set -uo pipefail
root=/home/hclau/ecdsa_research/widen-walk-20261015
census=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
cd "$root"; echo $$ > run.pid
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json 2>&1 || true
one() {
  local name=$1; shift
  python3 prepare.py "$name" "$@" > "$name.prepare.log" 2>&1 || { echo "prepare_exit=1" > "$name/status.txt"; return; }
  cd "$root/$name/src-b3"
  ( ulimit -v 16777216; CARGO_TARGET_DIR="$root/$name/target" cargo build --release --locked --offline --bin build_circuit ) > ../build.log 2>&1; echo "build_exit=$?" > ../status.txt
  sha256sum "$root/$name/target/release/build_circuit" > ../binary.sha256
  ( ulimit -v 16777216; /usr/bin/time -v "$root/$name/target/release/build_circuit" ) > ../generation.log 2>&1; echo "gen_exit=$?" >> ../status.txt
  if [ -s ops.bin ]; then
    sha256sum ops.bin > ../stream.sha256
    /usr/bin/time -f "wall=%e rss_kb=%M exit=%x" "$census" ops.bin "widen-$name" 0 4096 8 ../census.jsonl 2> ../census.err; echo "census_exit=$?" >> ../status.txt
  fi
  cd "$root"
}
while read -r name a b c; do
  [ -z "$name" ] && continue; [ -e "$name" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "${PAR:-5}" ]; do sleep 5; done
  one "$name" "$a" "$b" "$c" &
done < variants.txt
wait; date -Is > run.exit
