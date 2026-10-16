"""Immutable terminal supplement; retain stream refs and split large archives."""
from pathlib import Path
import hashlib,json,tarfile,io,shutil,math
r=Path(__file__).resolve().parent;cache=r/'all70-cache67-20261016';native=r/'all70-native67-20261016';out=r/'all70-complete-20261016';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(out/'receipt.json').exists();complete=(native/'census-launcher.exit').exists()and(native/'census-launcher.exit').read_text().strip()=='0'
status={'status':'INCOMPLETE_PIPELINE_EVIDENCE_PRESERVED','score':None,'nonce_search_performed':False,'complete_fixed_census':complete}
if complete:
 summary=json.loads((native/'census-summary.json').read_text());assert summary['batches_each']==32768
 totals=[]
 for role in ['parent','candidate']:
  rows=[json.loads(line)for line in(native/f'{role}-census.jsonl').read_text().splitlines()];assert len(rows)==32768 and sorted(x['batch']for x in rows)==list(range(32768))and all(x['shots']==64 for x in rows)
  totals.append({'role':role,'failed_batches':sum(bool(x['failures'])for x in rows),'dirty_shots':sum(x['dirty_shots']for x in rows),'shots':sum(x['shots']for x in rows),'toffoli':sum(x['toffoli']for x in rows)})
  assert totals[-1]['failed_batches']==summary['failed_batches'][role]
 assert [x['dirty_shots']for x in totals]==summary['dirty_shots']
 status.update(status='TERMINAL_FIXED_COMPOSITE_GATE_PASS'if summary['failure_gate_pass']else'TERMINAL_FIXED_COMPOSITE_GATE_FAIL',summary=summary,independent_archive_recount=totals)
 receipt=json.loads((native/'NATIVE_RECEIPT.json').read_text());assert sha(native/'candidate/ops.bin')==receipt['native_stream_sha256']
 with tarfile.open(native/'point-add-source.tar.gz')as t:
  files={m.name.removeprefix('point_add/'):hashlib.sha256(t.extractfile(m).read()).hexdigest()for m in t.getmembers()if m.isfile()}
 assert files==receipt['source_files_sha256']
 (out/'RESULT.json').write_text(json.dumps(status,indent=2)+'\n')
 (out/'RESULT.md').write_text('Complete fixed ALL70+67 comparison\n\n'+status['status']+'; this is not an official resource record.\n\n'+f"Frozen candidate {summary['candidate_sha256']}. Both complete32768-batch/2097152-shot sources are preserved. Failed batches: parent{totals[0]['failed_batches']}, candidate{totals[1]['failed_batches']}; candidate dirty shots{totals[1]['dirty_shots']}. Paired measured saving {summary['paired_mean_T_saving']:.8f} +/- {summary['saving_standard_error']:.8f}T/shot. No nonce search or submission.\n")
else:
 (out/'RESULT.json').write_text(json.dumps(status,indent=2)+'\n')
 if(native/'candidate/src/point_add').exists():
  with tarfile.open(out/'incomplete-point-add-source.tar.gz','w:gz')as t:t.add(native/'candidate/src/point_add',arcname='point_add')
base_archive=r/'all70-base-native-evidence.tar.gz';assert sha(base_archive)=='0c9afdc441dd7801524aea236f3d46f2c84b9eae2e92d4e004ea1cb1dad79258'
with tarfile.open(base_archive)as t:base=json.load(t.extractfile('manifest.json'))['files']
files=[];refs=[];oldrefs=[]
def add(p):
 if not p.is_file()or'__pycache__'in p.parts:return
 key=p.relative_to(r).as_posix();digest=sha(p)
 if key in base and digest==base[key]['sha256']:oldrefs.append({'path':key,'sha256':digest,'base_archive_sha256':sha(base_archive)});return
 if p.suffix=='.bin'and p!=native/'candidate/ops.bin':refs.append({'path':key,'sha256':digest,'bytes':p.stat().st_size});return
 files.append(p)
for directory in [cache,native]:
 for p in directory.rglob('*'):
  if directory==native and 'candidate'in p.relative_to(native).parts:continue
  add(p)
if(native/'candidate/ops.bin').exists():add(native/'candidate/ops.bin')
for p in r.iterdir():
 if p.is_file()and'all70'in p.name.lower()and p.suffix in ['.py','.sh','.json','.md','.log']:add(p)
for p in out.iterdir():
 if p.is_file()and p.name not in ['collect.log','launcher.exit']:add(p)
copies=out/'trusted-tools';copies.mkdir(exist_ok=False)
for name in ['flags-tool','cache-certificate-v2-tool','anchored-replay']:
 shutil.copytree(r/name,copies/name,ignore=shutil.ignore_patterns('target'))
for source,name in [(r/'target-flags/release/product_paired_diagnostic','generator'),(r/'target-cache-certificate-v2/release/product_paired_diagnostic','universal-verifier'),(r/'target-anchored-replay/release/product_paired_diagnostic','anchored-diagnostic')]:shutil.copyfile(source,copies/name)
shutil.copyfile(r/'cache-certificate-v2-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json',copies/'trusted-kernel-provenance-certificate.json')
for p in copies.rglob('*'):add(p)
files=list(dict.fromkeys(files));manifest={'status':status['status'],'files':{p.relative_to(r).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'prior_archive_file_refs':oldrefs,'retained_server_stream_hashrefs':refs,'base_archive':{'path':str(base_archive),'sha256':sha(base_archive)},'old_reference_stream':{'path':str(r/'tip/ops.bin'),'sha256':sha(r/'tip/ops.bin')},'no_nonce_no_submission':True};raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(out/'manifest.json').write_bytes(raw)
archive=out/'evidence.tar.gz'
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(archive,'r:gz')as t:
 for name,item in manifest['files'].items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
parts=[]
with archive.open('rb')as inp:
 for i in range(1,100):
  block=inp.read(40*1024**2)
  if not block:break
  p=out/f'evidence.part{i:02d}';p.write_bytes(block);parts.append({'file':p.name,'bytes':len(block),'sha256':sha(p)})
reassembled=hashlib.sha256()
for p in parts:reassembled.update((out/p['file']).read_bytes())
assert reassembled.hexdigest()==sha(archive)
result={'status':status['status'],'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'new_members':len(files),'prior_archive_references':len(oldrefs),'stream_hashrefs':len(refs),'parts':parts,'reassembly':'Concatenate evidence.partNN in numeric order as raw bytes, then verify archive_sha256; full canonical archive remains on server.','all_new_archived_hashes_verified':True,'no_nonce_no_submission':True};(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
