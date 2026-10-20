import hashlib,json,subprocess,sys,tarfile
from pathlib import Path
names=['breakthrough-targeted-ripple-width-20261020', 'breakthrough-targeted-ripple-width-v2-20261020', 'breakthrough-public-acd0-reproduction-20261020', 'breakthrough-public-acd0-exact-width-20261020']
ws=Path('/home/hclau/ecdsa_research');sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for name in names:
 r=ws/name
 if(r/'EVIDENCE-MANIFEST.json').exists():continue
 marker='controller.exit' if name=='breakthrough-public-e3-live-final-gate-20261020' else 'run.exit';assert(r/marker).exists(),(name,marker);terminal=(r/marker).read_text().strip();assert terminal in ['0','1'];files={};streams={};source_count=0
 if name=='breakthrough-public-e3-live-final-gate-20261020':assert terminal=='1' and not(r/'GATE-DECLARATION.json').exists() and not(r/'GATE-RESULT.json').exists()
 f=json.loads((r/'SOURCE-FREEZE.json').read_text()) if(r/'SOURCE-FREEZE.json').exists() else None
 if f and 'tool_source_files' in f:
  assert all(sha(r/'tool'/p)==h for p,h in f['tool_source_files'].items())
  for p in f['tool_source_files']:files['tool-source/'+p]=r/'tool'/p
 else:
  t=next((r/n for n in ['candidate','observer','parent'] if(r/n).is_dir()),None)
  if t:
   source={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};source_count=len(source);base=subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip();protected=[p for p in subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
   for p in protected:assert(t/p).read_bytes()==subprocess.check_output(['git','-C',str(t),'show','HEAD:'+p])
   if f:assert source==f['source_files'] and all(sha(t/p)==h for p,h in f['protected_files'].items())
   subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'preserved-source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
   with tarfile.open(r/'preserved-point-add-source.tar.gz','w:gz') as a:
    for p in sorted(source):a.add(t/p,arcname=p,recursive=False)
   (r/'PRESERVED-SOURCE-AUDIT.json').write_text(json.dumps({'status':'FROZEN_SOURCE_REVERIFIED' if f else 'PARTIAL_ASSEMBLY_FAILED_BEFORE_FREEZE_PRESERVED_AS_FOUND','base_revision':base,'source_files':source,'protected_files':{p:sha(t/p)for p in protected},'archive_sha256':sha(r/'preserved-point-add-source.tar.gz'),'patch_sha256':sha(r/'preserved-source.patch'),'scope':'Original failure retained. A postfailure snapshot is not a pre-test source freeze or passing candidate.'},indent=2)+'\n')
 for p in list(r.glob('parent/ops.bin'))+list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin'))+list(r.glob('*/raw.ops.bin')):streams[p.relative_to(r).as_posix()]=sha(p)
 audit={'ineligible_selector_mismatch':name in ['breakthrough-grouped-compact-width-v7-20261020','breakthrough-grouped-compact-width-v8-20261020'],'status':'SUPERSEDED_BEFORE_DECLARATION_NO_GATE_OR_CENSUS' if name=='breakthrough-public-e3-live-final-gate-20261020' else ('COMPLETED_RESEARCH_NOT_SCORED' if terminal=='0' else 'FAILED_RESEARCH_OR_PRE_FREEZE_ASSEMBLY_PRESERVED_NOT_SCORED'),'terminal_marker':marker,'terminal_exit':terminal,'source_files_checked':source_count,'source_freeze_present':f is not None,'scope':'Original outcomes final; no new gate/census/nonce/score. Failed partial sources are preserved separately and never recast as frozen passes.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
 for p in r.iterdir():
  if p.is_file() and 'resource-preflight' not in p.name and not p.name.endswith('ops.bin') and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[p.name]=p
 manifest={'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'audit':audit};(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
  for n,p in sorted(files.items()):a.add(p,arcname=n,recursive=False)
  a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
 (r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(name,len(files)+1,'sealed',flush=True)
