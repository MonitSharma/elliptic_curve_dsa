from pathlib import Path
import os,hashlib,json,tarfile,subprocess,shutil
p=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');tip=p.parent/'product-exact-20261015/tip';observer=p/'observer-tip';pref=p.parent/'prefilter-20261015';evidence=p/'independent-proof-receipts';evidence.mkdir(exist_ok=True)
names=['first-macro-688341-arbitrary.json','first-macro-688341-zero_reset.json','reset-projection-comparators.summary.json','reset-projection-comparators.jsonl','reset-projection-top1-complete.summary.json','reset-projection-top1-complete.jsonl']
proofs=[]
for name in names:
 src=pref/'evidence'/name
 if src.exists():shutil.copy2(src,evidence/name);proofs.append(src)
for name in ['reset_projection_symbols.rs','macro_proof_body.rs']:
 src=pref/'tool/src'/name
 if src.exists():shutil.copy2(src,evidence/name);proofs.append(src)
def digest(x):
 h=hashlib.sha256()
 with x.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
protected={}
for name in subprocess.check_output(['git','-C',str(tip),'ls-files'],text=True).splitlines():
 if name.startswith('src/point_add/'):continue
 a=tip/name;b=observer/name
 if a.is_file()and b.is_file():assert digest(a)==digest(b),name;protected[name]=digest(a)
external=[tip/'ops.bin',p.parent/'precision-repair-20261016/raw-builder.bin']+proofs;selected=[]
for base,dirs,names in os.walk(p):
 dirs[:]=[d for d in dirs if d not in ['target','.git','__pycache__']]
 for name in sorted(names):
  if name in ['.git','manifest.json','evidence.tar.gz','evidence.sha256']:continue
  x=Path(base)/name
  if x.stat().st_size>32*1024*1024 or name in ['ops.bin','raw-builder.bin']:external.append(x)
  else:selected.append(x)
manifest=dict(source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',protected_files_unchanged=protected,external={str(x):dict(bytes=x.stat().st_size,sha256=digest(x))for x in external},files={str(x.relative_to(p)):dict(bytes=x.stat().st_size,sha256=digest(x))for x in sorted(selected)})
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(p/'evidence.tar.gz','w:gz')as t:
 for x in sorted(selected)+[p/'manifest.json']:t.add(x,arcname=str(x.relative_to(p)),recursive=False)
(p/'evidence.sha256').write_text(digest(p/'evidence.tar.gz')+'  evidence.tar.gz\n');print((p/'evidence.sha256').read_text())
