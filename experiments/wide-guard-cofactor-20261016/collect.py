from pathlib import Path
import hashlib,json,tarfile,io,shutil,tomllib,subprocess
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (root/'run.exit').read_text().strip()=='0'
inp=root.parent/'wide15-record-20261016/evidence/final-ops.bin';assert sha(inp)=='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
kernel=root.parent/'current-value-attribution-20261016/donor-support-original.rs';assert sha(kernel)=='c262bba163fe91a6f2bd72e21fd387de84b426838b1bba113f017b18ed9cfa71'
assert (root/'tool/src/support.rs').read_bytes()==kernel.read_bytes()+b'\n'+(root/'cofactor.rs').read_bytes()
copy=root/'frozen-inputs';copy.mkdir(exist_ok=False)
shutil.copyfile(kernel,copy/'immutable-prefix-kernel.rs')
dependency=Path(tomllib.loads((root/'tool/Cargo.toml').read_text())['dependencies']['quantum_ecc']['path'])
for src,name in [(dependency/'src/circuit.rs','protected-circuit.rs'),(dependency/'Cargo.toml','dependency-Cargo.toml'),(root.parent/'product-exact-20261015/target-endpoint-census/release/value_prefilter','source-query-executable')]:shutil.copyfile(src,copy/name)
(root/'compiler.txt').write_bytes(subprocess.check_output(['/home/hclau/.cargo/bin/rustc','-Vv']))
files=[p for p in root.rglob('*') if p.is_file() and p.name not in ['evidence.tar.gz','manifest.json','receipt.json','collect.log']]
manifest={'files':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'hashrefs':[{'path':str(inp),'sha256':sha(inp),'bytes':inp.stat().st_size}]}
raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:
 for p in files:tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz') as tar:
 for name,item in manifest['files'].items():assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==item['sha256']
receipt={'status':'ALL_NEW_SOURCE_QUERY_ARTIFACTS_VERIFIED','members':len(files),'archive_bytes':(root/'evidence.tar.gz').stat().st_size,'archive_sha256':sha(root/'evidence.tar.gz'),'immutable_kernel_sha256':sha(kernel),'query_sha256':sha(root/'cofactor.rs'),'executable_sha256':sha(copy/'source-query-executable'),'source_stream_sha256':sha(inp)}
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
