"""Transfer a proved generic classical-factor pass to the public Toffoli base."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

candidate, original, evidence = map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip()=='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
assert not subprocess.check_output(['git','-C',str(candidate),'status','--porcelain'],text=True).strip()
expected={'classical_factors_xor.rs':'728a3c74279bee71f1e18b6f8d42e1e2d8a3c335e4c6ca01510643d8f4f57cf8',
          'product7_simplify.rs':'921045a6782ac053e4db074d698c89f03f67b6156f4fb98e8079be1c858c6258',
          'tests_classical_factors.rs':'825d06dade86bf43cd8a91e91b297582419add065d2dceca1c259d04ceeb81f8'}
for name,digest in expected.items():
    body=(original/'src/point_add'/name).read_bytes()
    assert hashlib.sha256(body).hexdigest()==digest,name
    (candidate/'src/point_add'/name).write_bytes(body)
p=candidate/'src/point_add/mod.rs';body=p.read_text();nonce_before=body[body.index('"TAIL_NONCE" =>'):].splitlines()[0]
assert body.count('mod truth_simplify;')==1
body=body.replace('mod truth_simplify;','mod truth_simplify;\nmod classical_factors_xor;')
needle='    let nonce: u64 = required_env("TAIL_NONCE");'
assert body.count(needle)==1
body=body.replace(needle,'    // Exact identities involving current classical bits; after bound passes.\n    ops = classical_factors_xor::simplify_classical(ops);\n'+needle)
assert body[body.index('"TAIL_NONCE" =>'):].splitlines()[0]==nonce_before
p.write_text(body,encoding='utf8')
files={}
for name in ['src/point_add/mod.rs']+['src/point_add/'+s for s in expected]:
    files[name]=hashlib.sha256((candidate/name).read_bytes()).hexdigest()
protected={}
for name in ['Cargo.lock','Cargo.toml','rust-toolchain','benchmark.sh','src/bin/build_circuit.rs','src/bin/eval_circuit.rs','src/circuit.rs','src/sim.rs','src/weierstrass_elliptic_curve.rs']:
    if (candidate/name).exists():
        body=(candidate/name).read_bytes()
        assert body==subprocess.check_output(['git','-C',str(candidate),'show','HEAD:'+name]),name
        protected[name]=hashlib.sha256(body).hexdigest()
assert all(s.startswith('src/point_add/') for s in subprocess.check_output(['git','-C',str(candidate),'diff','--name-only'],text=True).splitlines())
evidence.mkdir(parents=True,exist_ok=True)
(evidence/'source-binding.json').write_text(json.dumps({'baseline':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','source_sha256':files,'protected_sha256':protected,'tail_nonce':nonce_before,'nonce_changed':False,'scope':'Generic all-state classical factor identities transferred intact; generation and full unchanged benchmark required'},indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_sha256':files,'tail_nonce':nonce_before}))
