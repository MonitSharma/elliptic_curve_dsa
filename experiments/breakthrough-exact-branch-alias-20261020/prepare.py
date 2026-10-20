import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';ws=r.parent
assert not t.exists();t.mkdir()
old=ws/'breakthrough-guarded-lease-prover-20261020/tool'
shutil.copyfile(old/'io.rs',t/'io.rs');shutil.copyfile(r/'alias.rs',t/'alias.rs')
manifest='''[package]
name="exact_branch_alias"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={path="/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline"}
zstd="0.13"
sha3="0.10"
serde_json="1"
[[bin]]
name="exact_branch_alias"
path="alias.rs"
[profile.release]
opt-level=3
'''
(t/'Cargo.toml').write_text(manifest);shutil.copyfile(old/'Cargo.lock',t/'Cargo.lock')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
parent=ws/'public-product-54fc-20261020/parent/ops.bin';assert sha(parent)=='51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8'
dep=ws/'overnight-20261014/product-b3-baseline';protected=[dep/'Cargo.toml',dep/'Cargo.lock',dep/'src/circuit.rs',dep/'src/sim.rs',dep/'src/weierstrass_elliptic_curve.rs']
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'tool_source_files':{p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':{str(p):sha(p)for p in protected},'parent_stream_sha256':sha(parent),'parent':str(parent),'scope':'Read-only exact cancellation and branch-disjoint lifetime probe on exact public54fc stream. No nonce, census, arithmetic or measurement event changes. Incomplete proofs reject. Complement guard snapshots use full exact expressions; support cap overflows to universal, guard conjunction is uncapped.'},indent=2)+'\n')
