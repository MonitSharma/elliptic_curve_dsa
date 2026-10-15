#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > validate-v9-sequence.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/validate-v9-sequence.exit' EXIT
echo 'Waiting for our bounded source-bound generation job.'
for attempt in $(seq 1 120); do
 if test -e generate-v9.exit; then break; fi
 sleep 30
done
test "$(cat generate-v9.exit)" = 0
sha256sum --check stream-v9.sha256
echo 'Replaying the same three complete failed point additions.'
bash fixed-replay-v9.sh
echo 'Replaying all 9024 inputs from the existing failed packet; no new packet.'
bash fixed-packet-v9.sh
echo 'Fixed-packet diagnosis complete. This is not an official benchmark or submission.'
