"""Capture actual live identities without touching any running job or log."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;op=ws/'product-classical-nine-operational-20261019';gate=ws/'product-classical-twelve-native-20261019';final=ws/'classical9-final-20261019'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
profile=json.loads(subprocess.check_output(['python3',str(r/'preflight_v13.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
workers=[]
for lane in range(4):
    pid=int((op/f'worker{lane}.pid').read_text());proc=Path('/proc')/str(pid)
    item={'lane':lane,'pid':pid,'alive':proc.exists()}
    if proc.exists():
        item.update(executable=str((proc/'exe').resolve()),cwd=str((proc/'cwd').resolve()),threads=len(list((proc/'task').iterdir())))
        assert item['executable']==str(op/'tool/target/release/value_prefilter') and item['cwd']==str(op)
    item['progress']=json.loads((op/f'worker{lane}-progress.json').read_text());workers.append(item)
declaration=json.loads((gate/'qualification/DECLARATION.json').read_text());run=json.loads((op/'run-record.json').read_text())
snapshot={'at_utc':datetime.now(timezone.utc).isoformat(),'profile':profile,'run':run,'workers':workers,
 'completed_window_rows_reported':sum(x['progress']['cumulative_worker_rows'] for x in workers),'passing_nonce_files':len(list((op/'passes').glob('pass-*.json'))),
 'search_exit':(op/'search.exit').read_text().strip() if (op/'search.exit').exists() else None,
 'gate12':{'manager_pid':int((gate/'gate.pid').read_text()),'declaration_sha256':sha(gate/'qualification/DECLARATION.json'),'declared_at_utc':declaration['declared_at_utc'],'label':declaration['label'],'batch_count':declaration['batch_count'],'shots_per_batch':declaration['shots_per_batch'],'public_parent_id':declaration['public_parent']['id'],'streams':declaration['streams'],'gate_exit':(gate/'gate.exit').read_text().strip() if (gate/'gate.exit').exists() else None},
 'finalizer':{'watch_pid':int((final/'watch.pid').read_text()),'watch_source_sha256':sha(final/'WATCH_SOURCE.json'),'runtime_binding_sha256':sha(final/'RUNTIME-BINDING.json')},
 'scope':'Read-only live process and completed-window checkpoint. No terminal coverage audit or scored record.'}
p=r/'qualified-live-20261019T1455.json';assert not p.exists();p.write_text(json.dumps(snapshot,indent=2)+'\n');print(str(p))
