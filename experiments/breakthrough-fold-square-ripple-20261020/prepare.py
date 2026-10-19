import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-square-20261020'
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for name in['builder.rs','record.rs','break_profile.rs','mod.rs','y15_onefold.rs','width_composition.rs','parity_bridge.rs']:
    (t/'src/point_add'/name).write_bytes((old/'observer/src/point_add'/name).read_bytes())
p=t/'src/point_add/parity_bridge.rs';raw=p.read_bytes()
changes=[(b'for borrowed in[0,1,w-1]{',b'for(with_cin,borrowed)in[(true,0),(true,1),(true,w-1),(false,0),(false,1),(false,w-2)]{'),
 (b'let indices:Vec<_>=(0..borrowed).collect();assert!(add(&mut b,&target,&terms,Some(ci),&indices));',b'let first=usize::from(!with_cin);let indices:Vec<_>=(first..first+borrowed).collect();assert!(add(&mut b,&target,&terms,with_cin.then_some(ci),&indices));'),
 (b'let sum=av+(value>>w&mask)+(value>>(2*w+1)&1);',b'let sum=av+(value>>w&mask)+usize::from(with_cin)*(value>>(2*w+1)&1);')]
for before,after in changes:assert raw.count(before)==1;raw=raw.replace(before,after)
p.write_bytes(raw);(r/'carryout-tests-v2.rs').write_bytes(raw[raw.index(b'#[cfg(test)]mod carryout_tests'):])
p=t/'src/point_add/modular.rs';raw=p.read_bytes()
needle=b'    if go_copy0.is_some(){assert!(carry_in.is_none() && known_output.is_none() && owned>0);}'
assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    if go_copy0.is_none()&&c0==Carry0::Full&&c1==Carry1::Full&&deferred.is_none()&&known_output.is_none()&&known_terminal.is_none()&&borrowed.is_none(){
        if strict_square_ripple(circ,addend,acc,carry_in,carry_out){return;}
    }
''')
raw+=(r/'ripple-bridge.rs').read_bytes();p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'scope':'Add exact borrowing for full plain modular square ripples only. Preserve copy/deferred/known/borrowed carry contracts by excluding those calls. Both incoming-carry modes tested on arbitrary carryout high target. Original square planning retained; no score or final gate.'},indent=2)+'\n')
