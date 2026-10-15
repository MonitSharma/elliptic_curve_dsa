#!/usr/bin/env bash
# Census every candidate stream built on 15 Oct (plus C5 reference). Diagnostic; score=NONE.
set -uo pipefail
cd /home/hclau/ecdsa_research/failure-census-20261015
THREADS=${THREADS:-16}; BATCHES=${BATCHES:-4096}
mkdir -p results-all logs-all
{ date -Is; uptime; free -g; } > logs-all/preflight.txt
while read -r name path; do
  [ -s "results-all/$name.jsonl" ] && continue
  sha256sum "$path" > "results-all/$name.stream.sha256"
  /usr/bin/time -f "wall=%e rss_kb=%M exit=%x" target/release/failure_census "$path" "census-all-$name" 0 "$BATCHES" "$THREADS" "results-all/$name.jsonl" 2> "logs-all/$name.err"
  echo "$name exit=$?" >> logs-all/status.txt
done < streams-all.txt
date -Is > run-all.exit
