"""Preserve and stop only the explicitly named, owned low-yield SAT trial."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import sys

root=Path('/home/hclau/ecdsa_research/followup-20261015')
pid=int(sys.argv[1]);expected=str(root/'search-proved-resubstitution-v2.py')
cmd=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
actual=Path(cmd[1].decode())
if not actual.is_absolute():actual=(Path('/proc')/str(pid)/'cwd').resolve()/actual
assert actual.resolve()==Path(expected),cmd
query=root/'b3-resubstitution-v2/queries.jsonl'
counts=Counter();last=None
for line in query.read_text().splitlines():
    try:r=json.loads(line)
    except json.JSONDecodeError:continue
    counts[r['status']]+=1;last=r['op']
result=dict(status='stopped_partial_low_yield_search_not_complete_negative',pid=pid,
            stopped_at=datetime.now(timezone.utc).isoformat(),last_flushed_query_operation=last,
            flushed_query_counts=dict(counts),reason='Local cones produced repeated counterexamples and limits; prioritize the separately proved two-gate candidate.',
            source_sha256=hashlib.sha256(Path(expected).read_bytes()).hexdigest())
(root/'proof-search-v2-partial.json').write_text(json.dumps(result,indent=2)+'\n')
os.kill(pid,signal.SIGTERM)
print(json.dumps(result,indent=2))
