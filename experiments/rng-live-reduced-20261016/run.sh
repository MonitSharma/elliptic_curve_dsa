#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/rng-live-reduced-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > /home/hclau/ecdsa_research/rng-live-reduced-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 33554432
exe=/home/hclau/ecdsa_research/zero-mr-slice-20261016/tool/target/release/product_paired_diagnostic
program=/home/hclau/ecdsa_research/prefilter-20261015/evidence/certified-reduced-tip.ops.bin
sha256sum "$exe" "$program" > inputs.sha256
"$exe" "$program" /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv > reduced.log 2>&1
sha256sum -c inputs.sha256 > immutable-inputs.log
