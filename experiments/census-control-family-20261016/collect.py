from pathlib import Path
import hashlib,json,tarfile,io
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(root/'run.exit').read_text().strip()=='0'
assert sha(root/'ALL70.json')=='453e32f606d5dfaabbf12b4c7714c1cc986c5a6bdd534de3c76b123837d977d7'
summary=json.loads((root/'SUMMARY.json').read_text());assert summary['seed_same_row']==1 and summary['outside_A29_and_seed']==69
files=[p for p in root.rglob('*')if p.is_file() and '__pycache__'not in p.parts and p.name not in['evidence.tar.gz','receipt.json','manifest.json','collect.log']]
refs=[root.parent/'product-exact-20261015/tip/ops.bin',root.parent/'payload-model-20261016/before-census.bin']
manifest={'files':{p.relative_to(root).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'hashrefs':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}for p in refs]};raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(root).as_posix(),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz')as t:
 for name,item in manifest['files'].items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
receipt={'status':'ALL144_REPLAY_ALL70_INVENTORY_AND_CORRECTED_METADATA_VERIFIED','members':len(files),'archive_sha256':sha(root/'evidence.tar.gz'),'archive_bytes':(root/'evidence.tar.gz').stat().st_size,'no_candidate_no_sampling':True,'ALL70_sha256':sha(root/'ALL70.json')};(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
