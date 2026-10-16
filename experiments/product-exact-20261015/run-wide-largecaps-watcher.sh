#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > wide-largecaps-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/wide-largecaps-watcher.exit"' EXIT
while [ ! -f wide-to95-rank-20261016/launcher.exit ]; do sleep 20; done
test "$(cat wide-to95-rank-20261016/launcher.exit)" = 0
python3 freeze95.py wide > wide95-freeze.log
python3 prepare_wide151.py > wide151-abandoned-plan-preparation.log
test -f wide-to151-rank-20261016/ABANDONED.json
python3 prepare_wide_large_caps.py > wide-largecaps-plan.log
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-largecaps-20261016/admission-preflight.json
python3 -c 'from pathlib import Path; rows=dict(line.split(":",1) for line in Path("/proc/meminfo").read_text().splitlines()); assert int(rows["MemAvailable"].split()[0])*1024 >= 200*1024**3, "conservative200GiB available admission"'
# Replace the terminal wide95 one-core/24GiB slot; no extra parallel worker.
nohup setsid bash run-wide-large-caps.sh > wide-largecaps-20261016/nohup.log 2>&1 < /dev/null &
echo $! > wide-largecaps-20261016/nohup.pid
echo LARGE_CAP_PROBES_LAUNCHED_WIDE151_REMAINS_ABANDONED
