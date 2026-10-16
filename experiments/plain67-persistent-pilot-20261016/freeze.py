from pathlib import Path
import hashlib,json,statistics,tarfile

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
code=int((R/'run.exit').read_text().strip())
pins=json.loads((R/'RUNTIME-BINDINGS.json').read_text())
refs={pins['executable']:pins['executable_sha256'],**pins['artifacts']}
for path,h in refs.items():assert sha(path)==h,path
summary={'status':'DISABLED_UNCHANGED_PLAIN67_COST_TERMINAL','run_exit':code,
 'executable_sha256':pins['executable_sha256'],'source_sha256':'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',
 'search_authority':False,'nonce_selected':None,'production_changed':False,
 'co_tenancy':'Original25 search had terminated before the pilot timing trials; its48 worker cores were released. Preserve the captured resource snapshot. Different co-tenancy prevents a causal comparison against earlier repaired67 timings.',
 'forecast_scope':'Actual four-core group wall includes startup amortized over four4096 windows per worker. Scaling by16 to64 threads is ideal linear extrapolation, not measured64-thread scalability. Program-only walls exclude startup and are not an aligned common steady-state measurement.'}
if code==0:
 result=json.loads((R/'RESULT.json').read_text());assert result['all65536trial_rows_equal']
 assert json.loads((R/'SOURCE-PINS-BEFORE.json').read_text())==json.loads((R/'SOURCE-PINS-AFTER.json').read_text())
 reference=None
 for mode_index,mode in enumerate(['generic','direct']):
  for worker in range(2):
   path=R/f'trial{mode_index}-{mode}-worker{worker}.jsonl'
   rows=sorted(map(json.loads,path.read_text().splitlines()),key=lambda x:x['nonce'])
   assert len(rows)==16384 and [x['nonce']for x in rows]==list(range(1,16385))
   assert all(x['proof_accepted']is False and x['authoritative_rejection']is False for x in rows)
   if reference is None:reference=rows
   else:assert rows==reference,path
 for mode in ['generic','direct']:
  controls=sorted(map(json.loads,(R/f'control-{mode}-worker0.jsonl').read_text().splitlines()),key=lambda x:x['nonce'])
  assert controls==reference[4096:4107]
 for path in R.glob('*-mapped-libraries.json'):
  for item in json.loads(path.read_text()).values():assert item['actual_mapped_scalar_sha256']=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
 trials=[x for x in result['trials']if x['name'].startswith('trial')];assert len(trials)==2
 summary.update(status='DISABLED_UNCHANGED_PLAIN67_COST_AND_PROTOCOL_CONTROLS_PASS',
  all65536complete_trial_rows_equal=True,all22partial_control_rows_equal=True,
  expected_nonces_model=result['expected_nonces_model'],trials=trials,
  no_causal_generic_direct_speedup_claim=True,
  prior4096_qualification_archive_sha256='9f3923817a8175babb68ee992bf4da5593ffa3c5c36a6c297b7ad7897b48bfee')
else:summary['outcome']='INCOMPLETE_OR_FAILED_NO_COST_ACCEPTANCE'
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'SERVER-HASHREFS.json').write_text(json.dumps(refs,indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and p.name not in('evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')]
manifest={str(p.relative_to(R)):sha(p)for p in files}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as tar:
 for path in sorted(files+[R/'MANIFEST.json']):tar.add(path,arcname=str(path.relative_to(R)))
with tarfile.open(R/'evidence.tar.gz')as tar:
 for name,h in manifest.items():assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==h,name
receipt={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(manifest),
 'server_hashrefs':len(refs),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json')}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
