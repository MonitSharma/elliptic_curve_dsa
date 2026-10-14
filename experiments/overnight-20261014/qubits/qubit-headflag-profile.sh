#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/headflag-profile.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/headflag-profile.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/headflag-profile-preflight.json
for variant in candidate-n275-v2 candidate-headflag-v1; do
  dest="headflag-profile-$variant"
  python3 qubit-create-headflag-profile.py "$variant" base "$dest"
  export CARGO_TARGET_DIR="/home/hclau/ecdsa_research/overnight-20261014/qubits/$dest/target"
  cargo +1.93.0 generate-lockfile --offline --manifest-path "$dest/Cargo.toml"
  /usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path "$dest/Cargo.toml" > "evidence/$dest.log" 2>&1
  sha256sum "$dest/src/main.rs" "$dest/target/release/qubit_headflag_profile_${dest//-/_}"
done
