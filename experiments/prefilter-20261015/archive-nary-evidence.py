from pathlib import Path
import hashlib,json,tarfile,datetime
r=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for stem in ['mask-nary-profile','mask-nary8-compile','mask-nary8-validate','mask-nary8-fast-validate','mask-kernel-interleaved']:assert (r/'evidence'/(stem+'.exit')).read_text().strip()=='0'
reports={p.name:json.loads(p.read_text()) for p in [r/'evidence/mask-nary-profile.json',r/'evidence/mask-nary8-verification.json',r/'evidence/mask-nary8-runtime.json',r/'evidence/mask-nary8-fast-runtime.json',r/'evidence/mask-kernel-interleaved.json']}
receipt=dict(status='SEMANTIC_PASSES_PERFORMANCE_NEGATIVES_MRSLOT02_STILL_SELECTED',source_mask_sha256='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d',selected_plan_sha256='1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a',selected_library_sha256='dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0',reports=reports,libraries={p.name:sha(p) for p in [r/'libmask_nary8.so',r/'libmask_nary8_fast.so']},created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(r/'evidence/nary-runtime-negative-freeze.json').write_text(json.dumps(receipt,indent=2)+'\n')
def match(p):return any(x in p.name for x in ['nary8','nary-profile','mask-nary','kernel-interleaved','nary-evidence','nary-runtime','compare-mask-kernels'])
selected=[];large=[]
for p in list((r/'evidence').glob('*'))+list(r.iterdir()):
 if p.is_file() and match(p):
  if p.suffix=='.bin' or p.suffix=='.so':large.append(dict(path=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=sha(p)))
  elif p.suffix not in ['.gz']:selected.append(p)
selected.extend([r/'STATUS.md',r/'verify-evidence.py',r/'evidence/provenance.json'])
selected=sorted(set(selected));files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in selected}
manifest=r/'evidence/nary-archive-manifest.json';manifest.write_text(json.dumps(dict(included=len(files),files=files,excluded_large_files=large,excluded_active_files=[],terminal_checkpoint=True,base_checkpoint_archives={'evidence-local.tar.gz':'2787c3050d4cc6ddfd9e16325ccd48ad735314faee0f58442ae59ee6de6376e7','evidence-accelerator-supplement.tar.gz':'5e2c52415aa007cfc9f137492ac799ce503fbd7b39c05d92cc7382bea2585e23'}),indent=2)+'\n')
p=r/'evidence-nary-supplement.tar.gz'
with tarfile.open(p,'w:gz') as t:
 for f in selected:t.add(f,arcname=str(f.relative_to(r)),recursive=False)
 t.add(manifest,arcname='evidence/local-archive-manifest.json',recursive=False)
(r/(p.name+'.sha256')).write_text(sha(p)+'  '+p.name+'\n')
(r/'evidence/archive-nary-supplement.exit').write_text('0\n')
print(json.dumps(dict(archive=p.name,bytes=p.stat().st_size,sha256=sha(p),files=len(files),server_only_binary_hashrefs=len(large))))
