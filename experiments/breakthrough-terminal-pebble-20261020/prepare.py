import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';old=ws/'breakthrough-phase-pebble-paused-20261020';zero=ws/'breakthrough-phase-pebble-zero-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());zf=json.loads((zero/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'and(zero/'run-v2.exit').read_text().strip()=='0'
for source,freeze in[(old,f),(zero,zf)]:assert all(sha(source/'primitive'/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'primitive/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'primitive');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
(t/'src/point_add/zero_carry.rs').write_bytes((zero/'primitive/src/point_add/zero_carry.rs').read_bytes());(t/'src/point_add/terminal_pebble.rs').write_bytes((r/'terminal_pebble.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as out:out.write(b'\nmod zero_carry;\nmod terminal_pebble;\n')
p=t/'src/point_add/phase_pebble.rs';raw=p.read_bytes()
def change(needle,replacement):
 global raw
 assert raw.count(needle)==1,(needle,raw.count(needle));raw=raw.replace(needle,replacement)
change(b'false,&mut|_,_,_|{},None)',b'false,&mut|_,_,_|{},None,None)')
change(b'false,hook,None)',b'false,hook,None,None)')
change(b'true,hook,Some(mid))',b'true,hook,Some(mid),None)')
change(b'mid:Option<&mut dyn FnMut(&mut Builder,&[Option<QubitId>])>)->bool{',b'mid:Option<&mut dyn FnMut(&mut Builder,&[Option<QubitId>])>,desired:Option<bool>)->bool{')
change(b'    if let Some(mid)=mid{mid(c,&cc);}else{',b'    if let Some(desired)=desired{known_phase(c,acc,rows,ones,cc[m].unwrap(),desired);}else if let Some(mid)=mid{mid(c,&cc);}else{')
change(b'    for i in(0..n).rev(){\n        if drops.contains(&i)',b'    for i in(0..n).rev(){\n        if desired.is_some()&&i==n-1{continue;}\n        if drops.contains(&i)')
raw+=(r/'known_top.rs').read_bytes();p.write_bytes(raw)
with(t/'src/point_add/modular.rs').open('ab')as out:out.write((r/'tests.rs').read_bytes())
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'primitive/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'scope':'Known-top measured-output channel, preserving forced top even off promise. Compare exact original modular ripple on arbitrary basis inputs, zero/live cin, padding, both desired bits, guards and semantic measurement/reset-word alignment. Component only before integration, no finalgate/nonce/score/novelty claim.'},indent=2)+'\n')
