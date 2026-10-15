#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/zero-mr-20261016
test "$(cat run.exit)" = 0
cc -O3 -march=skylake-avx512 -fPIC -shared -Itool zero8.c -o libzero8-new.so
mv -f libzero8-new.so libzero8.so
sha256sum zero8.c main.rs libzero8.so > published.sha256
