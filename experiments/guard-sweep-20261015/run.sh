#!/usr/bin/env bash
# Guard-bit sweep on the wide (cap1536) B3 research base. Env-only HEO_PIN overrides;
# no source change. Measures executed-T cost vs honest failure rate. Diagnostic; score=NONE.
set -uo pipefail
root=/home/hclau/ecdsa_research/guard-sweep-20261015
src=/home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3
census=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
cd "$root"
echo $$ > sweep.pid
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json 2>&1 || true
if [ ! -d base ]; then echo "base missing: prepare base first" >&2; exit 2; fi
if true; then
  :
  (cd base && git diff --binary > ../base.patch) || true
  (cd base && cargo build --release --locked --offline --bin build_circuit) > build.log 2>&1
  sha256sum target/release/build_circuit > binary.sha256
fi
bin="$root/target/release/build_circuit"
run_variant() {  # name "PIN=VAL PIN=VAL"
  local name=$1 pins=$2 d="$root/v/$1"
  mkdir -p "$d"; cd "$d"
  echo "$pins" > pins.txt
  local envs=(HEO_RESEARCH=1)
  envs+=("GUARD_SWEEP_OVR=$(echo $pins | tr " " ";")")
  ( ulimit -v 16777216; env "${envs[@]}" /usr/bin/time -v "$bin" > generation.log 2>&1 ); echo "gen_exit=$?" > status.txt
  if [ -s ops.bin ]; then
    sha256sum ops.bin > stream.sha256
    /usr/bin/time -f "wall=%e rss_kb=%M exit=%x" "$census" ops.bin "guard-sweep-$name" 0 2048 6 census.jsonl 2> census.err
    echo "census_exit=$?" >> status.txt
    rm -f ops.bin.keep
  fi
  cd "$root"
}
export -f run_variant; export root bin census
while read -r name pins; do
  [ -z "$name" ] && continue
  [ -f "v/$name/status.txt" ] && continue
  sem_wait() { while [ "$(jobs -rp | wc -l)" -ge "${PAR:-6}" ]; do sleep 5; done; }
  sem_wait
  run_variant "$name" "$pins" &
done < variants.txt
wait
date -Is > sweep.exit
