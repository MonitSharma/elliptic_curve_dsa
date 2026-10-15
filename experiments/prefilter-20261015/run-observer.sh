#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/observer.exit' EXIT
echo $$ > evidence/observer.pid
ulimit -v 62914560
export PATH=/home/hclau/.cargo/bin:$PATH
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/prefilter-20261015/observer-target
uptime > evidence/observer.resources
free -g >> evidence/observer.resources
ps -eo pid,comm,pcpu,pmem,args --sort=-pcpu | head -20 >> evidence/observer.resources
python3 prepare-observer.py > evidence/observer.prepare.log 2>&1
cd observer-tip
cargo build --release --locked --offline --bin build_circuit > ../evidence/observer.build.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../evidence/observer.log 2>&1
sha256sum ops.bin > ../evidence/observer-stream.sha256
grep -q 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../evidence/observer-stream.sha256
