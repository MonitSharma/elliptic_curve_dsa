#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/phase-anchors
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/prefix40.exit"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 8388608
date -u
hostname
sha256sum /home/hclau/ecdsa_research/overnight-20261014/product-prefix-replay/src/main.rs "$evidence/ops.bin" "$evidence/anchors40.json" > "$evidence/prefix40-source.sha256"
cuts=$(python3 -c 'import json,sys; j=json.load(open(sys.argv[1])); print(",".join(x["phase"]+":"+str(x["prefix_end"]) for x in j["selected"] if x["raw_distance"]==0))' "$evidence/anchors40.json")
/usr/bin/time -v /home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis/target/release/product_prefix_replay "$evidence/ops.bin" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv "$cuts"
date -u
