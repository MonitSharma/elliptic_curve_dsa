#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/fold-selected.exit' EXIT
echo $$ > evidence/fold-selected.pid
ulimit -v 62914560
python3 select-fold-cases.py > evidence/select-fold-cases.log 2>&1
python3 walk_model.py evidence/fold-selected.tsv evidence/fold-selected.jsonl 999999 --folds > evidence/fold-selected.log 2>&1
