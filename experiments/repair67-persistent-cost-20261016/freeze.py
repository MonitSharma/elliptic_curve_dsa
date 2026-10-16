from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(R/'run.exit').exists();code=int((R/'run.exit').read_text().strip())
pins=json.loads((R/'LAUNCH_BINDINGS.json').read_text());assert sha(Path(pins['executable']))==pins['executable_sha256']
refs={pins['executable']:pins['executable_sha256']}
for item in pins['artifacts']:assert sha(Path(item['path']))==item['sha256'];refs[item['path']]=item['sha256']
summary={'status':'DISABLED_PERSISTENT_COST_TERMINAL','run_exit':code,'authority':False,'binary_sha256':pins['executable_sha256'],
 'scope':'Four fixed trials, four workers each, two threads per worker. Each worker replays the same existing16384 nonces in four4096 windows. No new unique inputs, source changes or search authority.',
 'forecast_scope':'An ideal linear64-thread projection from actual8-thread amortized wall time is a model, not a measured64-thread result. Individual program-only times exclude startup and do not measure an aligned common steady state.',
 'original_proposal_unchanged':True,'active25_unchanged':True}
if code==0:
 d=json.loads((R/'RESULT.json').read_text());assert d['status']=='DISABLED_PERSISTENT_FOUR_WINDOW_COST_AND_COMPLETE_ROWS_PASS'
 assert len(d['trials'])==4 and all(x['rows_with_repetitions']==65536 for x in d['trials'])
 assert json.loads((R/'SOURCE-PINS-BEFORE.json').read_text())==json.loads((R/'SOURCE-PINS-AFTER.json').read_text())
 summary['median_group_seconds']=d['median_group_seconds'];summary['ideal_linear_64_thread_mean_hours_NOT_MEASURED']=d['ideal_linear_64_thread_mean_hours_NOT_MEASURED']
 summary['all262144complete_rows_equal_frozen16384reference']=True
else:summary['outcome']='INCOMPLETE_OR_FAILED_NO_PERFORMANCE_ACCEPTANCE'
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'SERVER-HASHREFS.json').write_text(json.dumps(refs,indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and p.name not in('evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')]
manifest={str(p.relative_to(R)):sha(p)for p in files};(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as t:
 for p in sorted(files+[R/'MANIFEST.json']):t.add(p,arcname=str(p.relative_to(R)))
with tarfile.open(R/'evidence.tar.gz')as t:
 for name,h in manifest.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==h,name
receipt={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(manifest),'server_hashrefs':len(refs),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json')}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
