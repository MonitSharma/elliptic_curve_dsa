#!/usr/bin/env bash
# Slow-walk shape data: extra random chunks, then margin/trajectory runs. Diagnostic; score=NONE.
set -uo pipefail
base=/home/hclau/ecdsa_research/widen-walk-20261015
tv=/home/hclau/ecdsa_research/trace-value-20261015
cd "$base"; echo $$ > shape.pid
for c in 1 2 3; do
  [ -s "$tv/random8192-c$c.tsv" ] || python3 "$tv/gen_random.py" 8192 "$tv/random8192-c$c.tsv" /home/hclau/ecdsa_research/guard-sweep-20261015 $((c*1000000)) &
done
wait
sha256sum "$tv"/random8192*.tsv > random-chunks.sha256
run() { ./run-margin.sh "$1" "$2" "$3" > "margin-$1-$3.launcher.log" 2>&1; }
run mid4-smooth-anch4 random8192.tsv v2 &
run mid6-smooth-anch6 random8192.tsv v2 &
run mid2-smooth-anch2 random8192.tsv v2 &
run smooth random8192.tsv v2 &
run smooth random8192-c1.tsv c1 &
run smooth random8192-c2.tsv c2 &
run smooth random8192-c3.tsv c3 &
wait
date -Is > shape.exit
