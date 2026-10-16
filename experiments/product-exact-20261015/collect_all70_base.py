from pathlib import Path
import hashlib,json,tarfile,io,shutil
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert(d/'base-launcher.exit').read_text().strip()=='0'
receipt=json.loads((d/'BASE_NATIVE_RECEIPT.json').read_text());tree=r/'candidate-all70-base';assert sha(tree/'ops.bin')==receipt['source_sha256']
copies=d/'base-protected-inputs';copies.mkdir(exist_ok=False)
for name,digest in receipt['protected_files_sha256'].items():
 p=tree/name;assert sha(p)==digest;dest=copies/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
shutil.copyfile(tree/'target/release/build_circuit',copies/'native-build-circuit-executable')
files=[]
for p in d.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(d);name=rel.parts[0]
 if name.startswith('base-') or name.startswith('initial-cargo-') or name in ['BASE_NATIVE_RECEIPT.json','DECLARATION.json']:files.append(p)
files += [r/name for name in ['prepare_all70_base.py','verify_all70_base.py','run-all70-base.sh','resume-all70-base.sh','run_all70_cache67.py','watch-all70-cache67.sh','prepare_all70_native67.py','verify_all70_native67.py','watch-all70-native67.sh','qualify_all70_fixed67.py','watch-all70-census67.sh','collect_all70_base.py','PRODUCT67_FREEZE.json']]
refs=[tree/'ops.bin',r/'tip/ops.bin',r.parent/'payload-model-20261016/before-census.bin',r.parent/'census-control-family-20261016/evidence.tar.gz']
manifest={'status':'TERMINAL_BASE_ONLY_CACHE_AND_FRESH_GATE_PENDING','files':{p.relative_to(r).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'hashrefs':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}for p in refs]};raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(d/'base-archive-manifest.json').write_bytes(raw)
archive=r/'all70-base-native-evidence.tar.gz'
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(archive,'r:gz')as t:
 for name,item in manifest['files'].items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
record={'status':'ALL70_NATIVE_BASE_TERMINAL_SOURCE_LOGS_PROTECTED_FILES_VERIFIED','members':len(files),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'native_stream_sha256':receipt['source_sha256'],'cache_and_fresh_census':'pending','score':None};(r/'all70-base-native-evidence.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
