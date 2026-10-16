from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent;sha=lambda data:hashlib.sha256(data).hexdigest();a=r/'terminal-v1.tar.gz';receipt=json.loads((r/'terminal-v1-receipt.json').read_text());assert sha(a.read_bytes())==receipt['sha256']
with tarfile.open(a)as tf:
 m=json.load(tf.extractfile('terminal-v1/MANIFEST.json'))
 for name,v in m['files'].items():
  data=tf.extractfile('terminal-v1/'+name).read();assert len(data)==v['bytes']and sha(data)==v['sha256'],name
 for name,digest in m['base_pins'].items():
  p=Path(name);assert sha((r.parent/p.parent.name/p.name).read_bytes())==digest
 datasets=[]
 for role in ['parent','candidate']:
  rows={}
  for line in tf.extractfile('terminal-v1/seed-fresh/'+role+'.jsonl'):
   row=json.loads(line);batch=row['batch'];assert batch not in rows and 0<=batch<32768 and row['shots']==64
   fail=row['failures'];assert len({x['lane']for x in fail})==len(fail)and all(0<=x['lane']<64 for x in fail)
   for kind in ['value','phase','dirty']:assert sum(bool(x.get(kind,0))for x in fail)==row[kind+'_shots']
   rows[batch]=row
  assert len(rows)==32768;datasets.append(rows)
 x,y=datasets
 for batch in range(32768):
  before=x[batch];after=y[batch];assert after['toffoli']-before['toffoli']==64
  assert {k:v for k,v in before.items()if k!='toffoli'}=={k:v for k,v in after.items()if k!='toffoli'}
 counts=[]
 for rows in datasets:
  counts.append(dict(batches=32768,shots=2097152,failed_batches=sum(bool(v['failures'])for v in rows.values()),failed_shots=sum(len(v['failures'])for v in rows.values()),value_shots=sum(v['value_shots']for v in rows.values()),phase_shots=sum(v['phase_shots']for v in rows.values()),dirty_shots=sum(v['dirty_shots']for v in rows.values())))
 assert counts[0]==counts[1];count=counts[0];assert(count['failed_batches'],count['failed_shots'],count['value_shots'],count['phase_shots'],count['dirty_shots'])==(4214,4523,3622,2723,0)
 rate=count['failed_batches']*141/32768;assert rate>18
 out=dict(status='PASS INDEPENDENT LOCAL ARCHIVE AND COMPLETE RAW RECOUNT',archive_sha256=receipt['sha256'],verified_members=len(m['files']),base_pins_verified=len(m['base_pins']),external_streams=len(m['external']),parent=count,candidate=count,lambda_failed_batches_per9024=rate,all_rows_equal_except_exact64added_Toffolis_perbatch=True,strict_failure_gate_pass=False,cap_fail_both_parent_candidate=True,no_observed_failure_status_repairs_or_regressions=True,no_claim_all_incorrect_quantum_outputs_identical=True,no_resampling=True)
(r/'terminal-v1-local-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
