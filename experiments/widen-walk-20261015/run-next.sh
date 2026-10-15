#!/usr/bin/env bash
# Smooth-tail-only variant, then a first-divergence trace of its own value failures. Diagnostic; score=NONE.
set -uo pipefail
base=/home/hclau/ecdsa_research/widen-walk-20261015
cd "$base"; echo $$ > next.pid
PAR=1 ./run.sh > launcher-smooth.log 2>&1
[ -d trace-mid2-smooth ] && mkdir -p superseded && mv trace-mid2-smooth superseded/trace-mid2-smooth-parent-inputs
./run-trace.sh smooth > trace-smooth-launcher.log 2>&1
date -Is > next.exit
