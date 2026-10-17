#!/bin/bash
# PRODUCT179 phase B (user-approved 17 Oct: launch the search if the declared gate passes, ~96 threads
# while leaving other users enough capacity). Never submits.
set -euo pipefail
ws=/home/hclau/ecdsa_research; nd=$ws/product179-native-20261017
op=$ws/plain179-operational-20261017; fz=$ws/plain179-final-20261017; fl=$ws/product179-filter-20261017
cd "$nd"; echo $$ > chain-b.pid
trap 'echo $? > '"$nd"'/chain-b.exit' EXIT
log() { echo "$(date -Is) $*" >> "$nd/chain-b.log"; }
log "waiting for phase A"
while [ ! -e chain-a.exit ]; do sleep 60; done
test "$(cat chain-a.exit)" = 0
python3 -c "import json;g=json.load(open('GATE.json'));assert g['status']=='FAILURE_GATE_PASS',g['status']" || { log "gate did not pass; no search"; exit 0; }
log "gate PASS; generating phase B"
python3 make_phase_b.py > make-phase-b.log 2>&1
bash "$fl/run.sh"
test "$(cat $fl/run.exit)" = 0
python3 - <<'PY'
import hashlib,json
from pathlib import Path
f=Path('/home/hclau/ecdsa_research/product179-filter-20261017')
r=json.loads((f/'RESULT.json').read_text());assert r['status']=='DISABLED_PRODUCT179_PIPELINE_QUALIFICATION_PASS',r['status']
(f/'QUALIFIED_BASELINE.json').write_text(json.dumps({'baseline-0.jsonl':hashlib.sha256((f/'baseline-0.jsonl').read_bytes()).hexdigest(),'result_sha256':hashlib.sha256((f/'RESULT.json').read_bytes()).hexdigest()},indent=2)+'\n')
PY
log "filter qualified"
# Thread sizing: 4 workers x 14..24 threads, keeping at least 8 cores and the current load of other jobs free.
python3 - "$op" <<'PY'
import os,sys
from pathlib import Path
load=os.getloadavg()[1];cores=os.cpu_count()
each=max(14,min(24,int((cores-8-load)//4)))
avail=int(next(l.split()[1] for l in open('/proc/meminfo') if l.startswith('MemAvailable')))//(1024*1024)
assert avail>=100,avail
Path(sys.argv[1],'threads-each.txt').write_text(f'{each}\n')
Path(sys.argv[1],'threads-sizing.json').write_text(f'{{"loadavg5":{load},"cores":{cores},"threads_each":{each},"mem_available_gib":{avail}}}\n')
PY
log "threads $(cat $op/threads-sizing.json)"
cd "$op"
bash prepare-all.sh
test "$(cat prepare-all.exit)" = 0
log "acceptance and control passed"
(setsid nohup "$fz/watch.sh" > "$fz/watch-launch.log" 2>&1 < /dev/null &)
log "watcher armed; launching search"
bash run-search.sh
log "search finished: $(cat search.exit)"
