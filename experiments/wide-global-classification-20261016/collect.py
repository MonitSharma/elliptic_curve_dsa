from pathlib import Path
import hashlib,json,tarfile,io,shutil,tomllib
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert(root/'run.exit').read_text().strip()=='0'
kernel=(root/'immutable-kernel.rs').read_text();assert hashlib.sha256(kernel.encode()).hexdigest()=='c262bba163fe91a6f2bd72e21fd387de84b426838b1bba113f017b18ed9cfa71'
needle='let rewrite = Self::ccx_rewrite(&condition, &a, &b, op);';hook='\n                observe_global(&condition, &a, &b, op, &rewrite, self.condition_stack.len());';assert(root/'tool/src/support.rs').read_text()==kernel.replace(needle,needle+hook)+'\n'+(root/'observer.rs').read_text()
copy=root/'frozen-inputs';copy.mkdir(exist_ok=False);dependency=Path(tomllib.loads((root/'tool/Cargo.toml').read_text())['dependencies']['quantum_ecc']['path'])
for p,name in[(dependency/'src/circuit.rs','protected-circuit.rs'),(root.parent/'product-exact-20261015/target-endpoint-census/release/value_prefilter','source-query-executable')]:shutil.copyfile(p,copy/name)
files=[p for p in root.rglob('*')if p.is_file()and p.name not in['evidence.tar.gz','receipt.json','manifest.json','collect.log']]
refs=[root.parent/'wide-guard-cofactor-20261016/evidence.tar.gz',root.parent/'wide15-record-20261016/evidence/final-ops.bin']
manifest={'files':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'hashrefs':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}for p in refs]};raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz')as t:
 for p in files:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz')as t:
 for name,item in manifest['files'].items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
receipt={'status':'ALL43_CLASSIFIED_AND_ALL_NEW_ARTIFACTS_VERIFIED','members':len(files),'archive_bytes':(root/'evidence.tar.gz').stat().st_size,'archive_sha256':sha(root/'evidence.tar.gz'),'executed_T_saving_exact':0,'kernel_original_sha256':hashlib.sha256(kernel.encode()).hexdigest(),'source_query_sha256':sha(copy/'source-query-executable')};(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
