"""Preserve terminal failures/negatives without exporting resource process listings."""
import hashlib,json,re,subprocess,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1]
assert r.name in ['breakthrough-prefix-tick-canonical-20261020','breakthrough-prefix-bound-audit-20261020','breakthrough-public54fc-repeat-20261020']
assert not(r/'EVIDENCE-MANIFEST.json').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={};streams={};changed=[]
if 'bound-audit' in r.name:
 for name in ['run.exit','namespace.exit','window.exit']:assert(r/name).read_text().strip()=='0'
 a=json.loads((r/'CONTEXT-BINDING-AUDIT.json').read_text());w=json.loads((r/'WINDOW-AUDIT.json').read_text());n=json.loads((r/'NAMESPACE-AUDIT.json').read_text())
 assert a['table_edits']==82682 and len(a['unmapped_edits'])==78523 and w['mapped_count']==55657 and w['unmapped_count']==27025
 audit={'status':'READ_ONLY_PROOF_SUPPORT_AUDIT_INCOMPLETE_DO_NOT_TRANSPORT','whole_input_records':[a['old_source_input_count'],a['new_source_input_count']],'edits':82682,'common_region_mapped':4159,'common_region_unmapped':78523,'exact17record_window_mapped':55657,'exact17record_window_unmapped':27025,'namespace_counts':n['counts'],'scope':'No rewrites applied, no guard weakened, no resource result. Local window/opcode matches do not prove joint phase/measurement semantics; table has2547 CCX deletions and correlated transactions. Leave old module/table unchanged.'}
 for name in ['control.records.bin','mixed.records.bin']:streams[name]=sha(r/name)
else:
 t=r/'observer';f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
 if 'canonical' in r.name:
  assert(r/'run.exit').read_text().strip()=='1'and(r/'generate-control.exit').read_text().strip()=='0'and(r/'generate-mixed.exit').read_text().strip()=='101'
  assert sha(r/'control/ops.bin')=='51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8'
  log=(r/'generate-mixed.log').read_text();assert log.count('PREFIX_ALLOC_RESTORE tick=')==2 and 'left: 11442331' in log and 'right: 11453250' in log and 'src/bin/../point_add/square_finish.rs:13:1' in log
  for i,n in enumerate([1,1,1,1,1,2,2,1,1,2]):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-{i}.log').read_text())==[str(n)]
  audit={'status':'PUBLIC_CONTROL_EXACT_NATIVE_PASS_MIXED_STOP_AT_UNCHANGED_SQUARE_FINISH_BINDING','native_controls':13,'allocator_restorations':2,'allocator_gates_emitted':0,'binding_old_count':11453250,'binding_new_count':11442331,'scope':'Construction stop, not a final failure-rate gate, no nonce screening or benchmark. Both exact role/free-set allocator checks pass; Y42/linear_restore old guards pass; square_finish original count guard rejects. Every old source-bound module and table unchanged.'}
  for mode in ['control','mixed']:
   for p in(r/mode).iterdir():
    if p.is_file():
     if p.name.endswith('ops.bin'):streams[p.relative_to(r).as_posix()]=sha(p)
     else:files[p.relative_to(r).as_posix()]=p
 else:
  assert(r/'run.exit').read_text().strip()=='0';result=json.loads((r/'RESULT.json').read_text());assert result['diagnostic_saving']==0.0 and result['native_test_counts']==[3,3,4]
  def pretail(path):
   with path.open('rb',buffering=0)as source:
    header=source.read(16);assert header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');remain=(count-96)*56;h=hashlib.sha3_256();process=subprocess.Popen(['zstd','-dc'],stdin=source,stdout=subprocess.PIPE)
    while remain:
     chunk=process.stdout.read(min(remain,1<<20));assert chunk;h.update(chunk);remain-=len(chunk)
    tail=process.stdout.read();assert len(tail)==96*56 and process.wait()==0
   return count,h.hexdigest()
  parent=pretail(Path(f['public_input']));out=pretail(t/'ops.bin');assert parent==out
  audit={'status':'UNCHANGED_GENERIC_REPEAT_NO_CIRCUIT_GAIN','native_controls':10,'pretail_count':parent[0]-96,'pretail_records_sha3':parent[1],'parent_candidate_pretail_equal':True,'scope':'All canonical pre-tail records are identical. Only96-X identity nonce differs. No circuit improvement; do not gate/screen/submit. Static761061.742188 is diagnostic, not scored executed mean.'};streams['observer/ops.bin']=sha(t/'ops.bin')
 for p,h in f['source_files'].items():
  prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
  if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
 with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as archive:
  for p in sorted(changed):archive.add(t/p,arcname=p,recursive=False)
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']and not p.name.endswith('records.bin'):files[p.name]=p
manifest={'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p,v in sorted(files.items()):archive.add(v,arcname=p,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n')
print(r.name,len(files)+1,'members sealed',audit['status'],flush=True)
