import hashlib,json,re,subprocess,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1];assert r.name in ['breakthrough-prefix-tick-mixed-20261020','breakthrough-prefix-tick-alloc-20261020']and not(r/'EVIDENCE-MANIFEST.json').exists();t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());strict='tick-mixed'in r.name
if strict:
 assert(r/'run.exit').read_text().strip()=='1'and(r/'generate-mixed.exit').read_text().strip()=='101'and(r/'generate-control.exit').read_text().strip()=='0';assert sha(r/'control/ops.bin')=='51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8';assert'rebind y42_bound: region of 489932 ops found 0 times'in(r/'generate-mixed.log').read_text()
 for i,n in enumerate([1,1,1,1,1,2,2,1,1,2]):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-{i}.log').read_text())==[str(n)]
 audit={'status':'UNCHANGED_PUBLIC_CONTROL_EXACT_MIXED_STOPS_AT_LEGACY_REGION_BINDING','native_controls':13,'exact_public_control_sha256':sha(r/'control/ops.bin'),'failed_stage':'y42_bound unchanged region489932 not found','scope':'Construction/source-binding stop, not a declared final statistical gate, not a nonce-screening or benchmark verdict. Mixed candidate not verified or submitted. Every original bound assertion remains unchanged. Source/tests/failure/control evidence preserved before independent allocation diagnosis.'}
else:
 assert(r/'run.exit').read_text().strip()=='0';result=json.loads((r/'RESULT.json').read_text());assert result['stream_sha256']['control']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b';assert all(row['live_quantum_roles_equal']and row['active_qubit_counts_equal']and row['free_qubit_sets_equal']and row['held_classical_bit_sets_equal']and row['next_classical_counter_equal']for row in result['comparisons']);assert result['comparisons'][0]['free_qubit_orders_equal']and not result['comparisons'][1]['free_qubit_orders_equal']
 audit={'status':'EXACT_LIVE_INTERFACES_FREE_LIST_ORDER_DIFFERENT_AT_T130','native_controls_rerun':0,'comparisons':result['comparisons'],'scope':'Raw read-only allocator/interface capture only. Prior13 native controls belong to the strict-source experiment and are not rerun here. Tick129 state identical; tick130 live roles/free sets/counter identical, only free-list order differs. Supports trying existing asserted free-list restore, not proof of bound-pass transport or a resource result.'}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');changed=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as a:
 for p in sorted(changed):a.add(t/p,arcname=p,recursive=False)
files={p.name:p for p in r.iterdir()if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']};streams={}
for label in ['control','mixed']:
 for p in(r/label).iterdir():
  if p.is_file():
   if p.name.endswith('ops.bin'):streams[p.relative_to(r).as_posix()]=sha(p)
   else:files[p.relative_to(r).as_posix()]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p,v in sorted(files.items()):a.add(v,arcname=p,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1,'members sealed')
