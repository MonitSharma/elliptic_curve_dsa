import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines();protected={p:sha(t/p)for p in paths if not p.startswith('src/point_add/')};assert len(protected)==17
old=ws/'breakthrough-cap-cost-20261020/observer'
for name in['builder.rs','record.rs','break_profile.rs','mod.rs']:(t/'src/point_add'/name).write_bytes((old/'src/point_add'/name).read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def sub(old,new):
    global raw
    assert raw.count(old)==1,(old,raw.count(old));raw=raw.replace(old,new)
sub(b'const Y28_PLAN8:',b'const Y28_PLAN7: ([usize; 12], [usize; 5]) = ([7,6,6,5,5,4,4,3,3,2,2,3], [0,2,4,6,8]);\nconst Y28_PLAN8:')
sub(b'let need = fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45);',b'''let saving=if drop>=5{3}else{drop};
    let need = fixed + min_budget - saving - 2 * usize::from(Y15_LEAN45);''')
sub(b'let drop_n = if cut && !close && !swap01 && Y15_CORE_V2 { y28_drop(t, rev) } else { 0 };',b'''let drop_n = if cut && !close && !swap01 && Y15_CORE_V2 { y28_drop(t, rev) } else { 0 };
    let drop_n=if cells::cap()<=1233{match drop_n{1=>2,2=>5,n=>n}}else{drop_n};''')
sub(b'nbits == 50 && budget + drop >= 10 && (8..=9).contains(&budget)',b'nbits == 50 && (budget>=8&&budget+drop>=10 || budget==7&&drop>=5) && (7..=9).contains(&budget)')
needle=b'return if budget == 9 { (Y28_PLAN9.0.to_vec(), lean45, Y28_PLAN9.1.to_vec()) } else { (Y28_PLAN8.0.to_vec(), lean45, Y28_PLAN8.1.to_vec()) };'
sub(needle,b'return if budget==7{(Y28_PLAN7.0.to_vec(),lean45,Y28_PLAN7.1.to_vec())}else if budget == 9 { (Y28_PLAN9.0.to_vec(), lean45, Y28_PLAN9.1.to_vec()) } else { (Y28_PLAN8.0.to_vec(), lean45, Y28_PLAN8.1.to_vec()) };')
raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233,1232,1230],'scope':'Exact nonadjacent early-drop plan, native tests before capacity generation. No point-add arithmetic windows/iterations changed; no final correctness gate, nonce or resource score.'},indent=2)+'\n')
