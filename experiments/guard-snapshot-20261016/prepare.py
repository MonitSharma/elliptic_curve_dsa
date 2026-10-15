from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parent
assert not (r/'tool').exists()
(r/'tool/src').mkdir(parents=True)
shutil.copyfile(r/'main.rs',r/'tool/src/main.rs')
(r/'tool/Cargo.toml').write_text('[package]\nname="guard_snapshot_audit"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path="/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline"}\nsha3="0.10"\nserde_json="1"\n[profile.release]\nopt-level=3\n')
parent=r.parent/'overnight-20261014/product-b3-baseline'
expected={'src/sim.rs':'f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7','src/circuit.rs':'ac2255f6bcb6895c9da2dfe21c3a051a0ef8fc4e0af9598634fec0035dbf35c6'}
for name,h in expected.items():assert hashlib.sha256((parent/name).read_bytes()).hexdigest()==h,name
(r/'PROTECTED-INPUTS.json').write_text(json.dumps(expected,indent=2)+'\n')
