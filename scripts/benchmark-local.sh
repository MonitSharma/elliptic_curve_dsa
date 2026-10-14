#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
source ./activate.sh
mkdir -p research-output
log_path="research-output/benchmark-$(date '+%Y%m%d-%H%M%S').log"
./benchmark.sh "$@" 2>&1 | tee "$log_path"
printf '\nBenchmark log: %s\n' "$log_path"
