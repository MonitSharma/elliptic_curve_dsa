"""Raw arithmetic capacity sweep; no candidate, final gate or nonce search."""
import hashlib,json,subprocess
from pathlib import Path

r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer'
assert not t.exists()
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={name:sha(t/name) for name in paths if not name.startswith('src/point_add/')}
assert len(protected)==17
profile=ws/'breakthrough-profile-20261020/observer'
for name in ['builder.rs','record.rs','break_profile.rs']:
 (t/'src/point_add'/name).write_bytes((profile/'src/point_add'/name).read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes()
def sub(old,new):
 global raw
 assert raw.count(old)==1,(old,raw.count(old))
 raw=raw.replace(old,new)
sub(b'pub fn build() -> Vec<Op> {',b'''pub fn build() -> Vec<Op> {
    let break_cap = std::env::var("BREAK_CAP").expect("Diagnostic BREAK_CAP required");
    let parsed: usize = break_cap.parse().expect("Numeric diagnostic cap");
    assert!((1000..=1300).contains(&parsed));''')
sub(b'let mut ops = build_point_add();',b'''std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);
    std::env::set_var("LF_SQUARE_CAP", &break_cap);
    let mut ops = build_point_add();
    break_profile::save_ops("prepass.ops.bin", &ops);
    if true { return ops; } // Diagnostic raw arithmetic, before all post-passes.''')
raw+=b'\nmod break_profile;\n';p.write_bytes(raw)
assert all(sha(t/name)==h for name,h in protected.items())
freeze={'status':'RAW_ARITHMETIC_DIAGNOSTIC_ONLY','base':base,'caps':[1234,1200,1168,1136,1104],
 'protected_files':protected,'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Capacity settings frozen before all runs; no new cuts/tables or nonce. Raw cap1234 must match the admitted baseline prepass exactly. Native generation failures remain failed admission attempts.'}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'observer-source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
print('Capacity sweep prepared; protected17 unchanged.')
