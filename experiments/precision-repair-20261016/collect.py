from pathlib import Path
import os,hashlib,json,tarfile,subprocess,shutil
p=Path('/home/hclau/ecdsa_research/precision-repair-20261016');tip=p.parent/'product-exact-20261015/tip';candidate=p/'candidate-posttable-top1'
def digest(x):
 h=hashlib.sha256()
 with x.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def files():
 for base,dirs,names in os.walk(p):
  dirs[:]=[d for d in dirs if d not in ['target','.git','__pycache__']]
  for name in names:
   if name!='.git':yield Path(base)/name
tracked=subprocess.check_output(['git','-C',str(tip),'ls-files'],text=True).splitlines();protected={}
for name in tracked:
 if name.startswith('src/point_add/'):continue
 a=tip/name;b=candidate/name
 if a.is_file()and b.is_file():assert digest(a)==digest(b),name;protected[name]=digest(a)
source_json=p/'candidate-posttable-top1-source.json'
if source_json.exists()and not(p/'candidate-posttable-top1-source-v1.json').exists():shutil.copy2(source_json,p/'candidate-posttable-top1-source-v1.json')
source=dict(base='4b2ec52fc55da796aa8f5ef851290297e8706424',source_changes_only_point_add=True,all_inherited_tables_and_assertions_retained=True,protected_files_unchanged=protected,files={str(x.relative_to(candidate)):digest(x)for x in(candidate/'src/point_add').rglob('*')if x.is_file()})
source_json.write_text(json.dumps(source,indent=2)+'\n')
(p/'candidate-posttable-top1.patch').write_bytes(subprocess.check_output(['git','-C',str(candidate),'diff','--binary']))
excluded={'manifest.json','evidence.tar.gz','evidence.sha256'}
external=[p.parent/'prefilter-20261015/evidence/census-coordinates4096.tsv',tip/'ops.bin',p.parent/'failure-census-20261015/target/release/failure_census',p.parent/'failure-census-20261015/census/src/main.rs']
selected=[]
for x in sorted(files()):
 if x.name in excluded:continue
 if x.stat().st_size>32*1024*1024 or x.name=='ops.bin' or x.name.endswith('-ops.bin')or x.name=='raw-builder.bin':external.append(x)
 else:selected.append(x)
manifest=dict(base_revision=source['base'],protected_files_unchanged=protected,external={str(x):dict(bytes=x.stat().st_size,sha256=digest(x))for x in external},files={str(x.relative_to(p)):dict(bytes=x.stat().st_size,sha256=digest(x))for x in selected})
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(p/'evidence.tar.gz','w:gz')as t:
 for x in selected+[p/'manifest.json']:t.add(x,arcname=str(x.relative_to(p)),recursive=False)
(p/'evidence.sha256').write_text(digest(p/'evidence.tar.gz')+'  evidence.tar.gz\n');print((p/'evidence.sha256').read_text())
