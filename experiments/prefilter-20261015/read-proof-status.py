from pathlib import Path
import json
r=Path(__file__).parent/'evidence'
for p in sorted(r.glob('global-anf*-tip32.json')):
 if p.stat().st_size:
  x=json.loads(p.read_text());print(json.dumps(dict(file=p.name,**{k:x.get(k)for k in ['input_only_dag_nodes','unresolved_rng_dependent_bits','proved_value_rng_independent','seconds']})))
 else:
  log=p.with_suffix('.log');lines=log.read_text().splitlines()if log.exists()else[];print(p.name,lines[-1]if lines else'pending')
