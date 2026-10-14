#!/usr/bin/env bash
# Export this one completed failed stream's fixed packet; never alter its nonce.
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-headflag-fixed-packet-v1"
mkdir -p "$evidence"
echo "$$" > "$evidence/run.pid"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
native="$root/coordinator-stream-packet-v1/target/release/fixed_stream_packet"
stream="$root/qubits/evidence/headflag-v1-ops.bin"
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
test "$(cat "$root/qubits/evidence/headflag-v1-official-eval-native.exit")" = 1
test "$(cat "$root/coordinator-stream-packet-v1/run.exit")" = 0
test "$(sha256sum "$native" | cut -d' ' -f1)" = 28619c14c966cf4f384b2a77b34a9ad200ef697e4a2e48fa41263b70e7523245
test "$(sha256sum "$stream" | cut -d' ' -f1)" = 6b0046e2470cabf150fa6d2892e0b8206a683d3975b5d268cd7b80ed2cfdc902
sha256sum "$root/server-headflag-fixed-packet.sh" "$native" "$root/coordinator-stream-packet-v1/crate/src/main.rs" > "$evidence/source.sha256"
test ! -e "$evidence/headflag-v1-official-packet.tsv"
/usr/bin/time -v timeout 1800 "$native" export "$stream" "$evidence/headflag-v1-official-packet.tsv"
sha256sum "$evidence/headflag-v1-official-packet.tsv" "$evidence/headflag-v1-official-packet.tsv.batch37-rng-prefix.bin" > "$evidence/packet.sha256"
date -u
