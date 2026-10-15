from pathlib import Path
import hashlib,json,tarfile,subprocess,shutil
p=Path('/home/hclau/ecdsa_research/payload-model-20261016');tip=p.parent/'product-exact-20261015/tip';reference=p/'production-reference';reference.mkdir(exist_ok=True)
for name in ['leapfrog.rs','y15_onefold.rs','pingpong.rs','modular.rs','square.rs','census_cut_data.txt','census_anchors.txt','census_cut.rs','census_anchored.rs']:
 shutil.copy2(tip/'src/point_add'/name,reference/name)
def digest(x):
 h=hashlib.sha256()
 with x.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
server_only_names={'ops.bin','before-census.bin'}
external=[p.parent/'prefilter-20261015/evidence/census-coordinates4096.tsv',tip/'ops.bin']+sorted(x for x in p.rglob('*') if x.is_file()and x.name in server_only_names and 'target'not in x.parts)
protected={}
tracked=subprocess.check_output(['git','-C',str(tip),'ls-files'],text=True).splitlines()
for name in tracked:
 if name.startswith('src/point_add/'):continue
 a=tip/name;b=p/'observer-tip'/name
 if a.is_file()and b.is_file():
  ha,hb=digest(a),digest(b);assert ha==hb,(name,ha,hb);protected[name]=ha
manifest={'base_revision':'4b2ec52fc55da796aa8f5ef851290297e8706424','protected_files_unchanged':protected,'external':{str(x):{'bytes':x.stat().st_size,'sha256':digest(x)}for x in external},'files':{}}
excluded={'manifest.json','evidence.tar.gz','evidence.sha256'}|server_only_names
for x in sorted(p.rglob('*')):
 if x.is_file()and 'target'not in x.parts and '__pycache__'not in x.parts and x.name not in excluded:
  manifest['files'][str(x.relative_to(p))]={'bytes':x.stat().st_size,'sha256':digest(x)}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(p/'evidence.tar.gz','w:gz')as t:
 for x in sorted(p.rglob('*')):
  if x.is_file()and 'target'not in x.parts and '__pycache__'not in x.parts and x.name not in {'evidence.tar.gz','evidence.sha256'}|server_only_names:
   t.add(x,arcname=str(x.relative_to(p)))
(p/'evidence.sha256').write_text(digest(p/'evidence.tar.gz')+'  evidence.tar.gz\n');print((p/'evidence.sha256').read_text())
