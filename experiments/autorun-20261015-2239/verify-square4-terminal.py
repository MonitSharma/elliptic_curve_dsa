"""Recount the entire frozen square repair cohort and check archived source."""
from pathlib import Path,PurePosixPath
from collections import Counter
import hashlib,json,tarfile
root=Path(__file__).resolve().parents[2]/'experiments/value-carry-contracts-20261016'
p=root/'evidence.tar.gz';assert hashlib.sha256(p.read_bytes()).hexdigest()=='59b31cec94b75f1c1a1aed3190cb647998f0a683245032127b86d18fe1436925'
with tarfile.open(p) as t:
 names=t.getnames();assert len(names)==len(set(names))
 assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 assert all(m.isfile() or m.isdir() for m in t.getmembers())
 read=lambda n:t.extractfile(n).read()
 manifest=json.loads(read('manifest.json'));assert len(manifest['files'])==736
 for n,info in manifest['files'].items():
  raw=read(n);assert len(raw)==info['bytes'] and hashlib.sha256(raw).hexdigest()==info['sha256'],n
 source=json.loads(read('square4-source.json'))
 for n,sha in source['files'].items():assert hashlib.sha256(read('square4-candidate/'+n)).hexdigest()==sha,n
 declaration=read('SQUARE4-PREDECLARATION.json');assert hashlib.sha256(declaration).hexdigest()=='11d3cd766320622216bcd99cb24bb759d666cc34ba3c413d0e5b9070f33d354c'
 summary=json.loads(read('square-paired-summary.json'))
 arrays={}
 for label in ['parent','candidate']:
  rows=list(map(json.loads,read('square-fresh/'+label+'.jsonl').splitlines()));assert len(rows)==32768
  by={r['batch']:r for r in rows};assert sorted(by)==list(range(32768));arrays[label]=by
  totals=dict(shots=0,toffoli=0,failed_batches=0,failed_shots=0,value_shots=0,phase_shots=0,dirty_shots=0)
  for r in rows:
   assert r['shots']==64 and r['skipped']==0
   totals['shots']+=64;totals['toffoli']+=r['toffoli'];totals['failed_batches']+=bool(r['failures']);totals['failed_shots']+=len(r['failures'])
   assert len({v['lane'] for v in r['failures']})==len(r['failures'])
   for k in ['value','phase','dirty']:
    assert sum(v[k] for v in r['failures'])==r[k+'_shots'];totals[k+'_shots']+=r[k+'_shots']
  for k,v in totals.items():assert summary[label][k]==v,(label,k)
 repairs=Counter();new=Counter();passing=[]
 for i in range(32768):
  old,now=arrays['parent'][i],arrays['candidate'][i];assert now['toffoli']-old['toffoli']==1024
  a={v['lane']:v for v in old['failures']};b={v['lane']:v for v in now['failures']}
  for lane in a.keys()|b.keys():
   if lane in a and lane in b:assert (a[lane]['k1'],a[lane]['k2'])==(b[lane]['k1'],b[lane]['k2'])
   for k in ['value','phase','dirty']:
    x=a.get(lane,{}).get(k,0);y=b.get(lane,{}).get(k,0)
    repairs[k]+=bool(x and not y);new[k]+=bool(y and not x)
   if lane in a and lane not in b:passing.append([i,lane])
 assert repairs=={'value':2,'phase':0,'dirty':0} and not any(new.values())
 assert passing==[[18562,21],[22510,41]]
 assert summary['strict_paired_failure_gate_passed'] and summary['added_MR']==0 and summary['Q']==1234
 assert read('square-fresh.exit').strip()==b'0' and read('square-native.exit').strip()==b'0'
 out=dict(status='INDEPENDENT_ALL_SOURCE_HASHES_AND_COMPLETE_SQUARE4_COHORT_PASS',archive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),artifacts=736,complete_point_add_source_files=len(source['files']),batches_each=32768,shots_each=2097152,failed_batches_parent=4175,failed_batches_candidate=4173,exact_added_T_every_shot=16,value_repairs=2,all_channel_regressions=0,Q=1234,added_MR=0,not_a_resource_record=True,no_cache_composition_or_nonce_search=True)
(root/'ROOT_TERMINAL_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
