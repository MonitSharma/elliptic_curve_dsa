import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();rows=[];traces={}
for cap in f['caps']:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());case=r/f'cap{cap}';case.mkdir(exist_ok=False);env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD=str(cap));start=time.time()
 with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:
  p=subprocess.Popen(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (case/'generate.exit').write_text(str(rc)+'\n');assert rc==0;shutil.copyfile(t/'ops.bin',case/'ops.bin');assert sha(case/'ops.bin')==f['expected_raw_sha256'][str(cap)]
 traces[cap]=[l.split('\t')[1:]for l in(case/'generate.log').read_text().splitlines()if l.startswith('LAYOUT_AUDIT\t')];(case/'replay-sites.json').write_text(json.dumps(traces[cap],indent=2)+'\n');rows.append({'cap':cap,'exit':rc,'raw_sha256':sha(case/'ops.bin'),'trace_sites':len(traces[cap]),'trace_sha256':sha(case/'replay-sites.json'),'seconds':time.time()-start})
control=Counter(tuple(x)for x in traces[1234]);comparisons=[]
for cap in [1233,1232]:
 candidate=Counter(tuple(x)for x in traces[cap]);only_old=control-candidate;only_new=candidate-control
 comparisons.append({'cap':cap,'identical_ordered_trace':traces[cap]==traces[1234],'identical_site_multiset':candidate==control,'old_only_count':sum(only_old.values()),'new_only_count':sum(only_new.values()),'old_only_examples':list(only_old.items())[:20],'new_only_examples':list(only_new.items())[:20]})
report={'status':'EXACT_STREAM_CONTROLS_WITH_REPLAY_METADATA','cases':rows,'comparisons':comparisons,'scope':'Trace covers existing record_replay_site calls only. Any difference refutes a claim that all traced replay predicates are unchanged. Identical traces do not establish completeness for every approximation in the circuit. No full correctness census or resource score.'};(r/'LAYOUT-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
