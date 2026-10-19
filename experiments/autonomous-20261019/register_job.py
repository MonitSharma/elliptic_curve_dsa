"""Register a reviewed job's immutable sources before launching its leader."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from resource_registry import validated_spec
p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('--pidfile',required=True);p.add_argument('--exitfile',required=True);p.add_argument('--entrypoint',required=True);p.add_argument('--slots',type=int,required=True);p.add_argument('--kind',choices=['compute','idle'],required=True);a=p.parse_args()
ws=Path(__file__).resolve().parent.parent;r=ws/a.directory
assert not (r/a.pidfile).exists() and not (r/a.exitfile).exists(),'Never silently restart an existing job'
sources={q.relative_to(r).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted(r.iterdir()) if q.suffix in ['.py','.sh','.rs']}
record={'registered_at_utc':datetime.now(timezone.utc).isoformat(),'directory':a.directory,'pidfile':a.pidfile,'exitfile':a.exitfile,'entrypoint':a.entrypoint,'slots':a.slots,'kind':a.kind,'source_hashes':sources,'scope':'Reviewed research job reservation only; no gate, runtime acceptance or score is implied.'}
validated_spec(ws,record);folder=ws/'resource-registry-20261020';folder.mkdir(exist_ok=True);dest=folder/(a.directory+'-'+Path(a.pidfile).stem+'.json');assert not dest.exists()
with dest.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'descriptor':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'slots':a.slots}))
