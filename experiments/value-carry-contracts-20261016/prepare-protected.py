from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');d=r/'tool';s=d/'src/bin';s.mkdir(parents=True,exist_ok=True)
base=r.parent/'quantum-borrow-family-20261016/proof-tool'
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(base/name,d/name)
shutil.copy2(r/'protected_terminal.rs',s/'protected_terminal.rs')
ref=r.parent/'overnight-20261014/product-b3-baseline/src/sim.rs'
sha=hashlib.sha256(ref.read_bytes()).hexdigest();assert sha=='f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7'
(r/'protected-source.json').write_text(json.dumps(dict(simulator_path=str(ref),simulator_sha256=sha,tool={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in d.rglob('*')if p.is_file()}),indent=2)+'\n')
