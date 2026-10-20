import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-integration-20261020';zero=ws/'breakthrough-phase-pebble-zero-20261020';square=ws/'breakthrough-fold-square-short-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());zf=json.loads((zero/'SOURCE_FREEZE-v2.json').read_text());sf=json.loads((square/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'and(zero/'run-v2.exit').read_text().strip()=='0'
for parent,freeze,sub in[(old,f,'observer'),(zero,zf,'primitive'),(square,sf,'observer')]:assert all(sha(parent/sub/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
(t/'src/point_add/zero_carry.rs').write_bytes((zero/'primitive/src/point_add/zero_carry.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod zero_carry;\n')
with(t/'src/point_add/phase_fit.rs').open('ab')as stream:stream.write((r/'optional_adapter.rs').read_bytes())
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();start=raw.index(b'fn phase_plain_try(');end=raw.index(b'// The returned outer Option',start)
replacement=b'''fn phase_plain_try(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],cin:Option<QubitId>)->bool{
    let mut h=Y28_HOOK.with(|v|v.take());let before=c.op_count();
    if super::phase_fit::plain_optional(c,acc,rows,&vec![false;acc.len()],cin,&mut|c,i,q|y28_apply(c,&mut h,i,q)){
        assert!(h.is_none(),"phase optional carry hook not consumed");true
    }else{assert_eq!(before,c.op_count());Y28_HOOK.with(|v|v.set(h));false}
}
''';p.write_bytes(raw[:start]+replacement+raw[end:])
p=t/'src/point_add/modular.rs';raw=p.read_bytes();needle=b'    if go_copy0.is_some(){assert!(carry_in.is_none() && known_output.is_none() && owned>0);}';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    if go_copy0.is_none()&&c0==Carry0::Full&&c1==Carry1::Full&&deferred.is_none()&&known_output.is_none()&&known_terminal.is_none()&&borrowed.is_none(){
        if phase_plain_modular(circ,addend,acc,carry_in,carry_out){return;}
    }
''')
raw+=b'''
fn phase_plain_modular(c:&mut Builder,a:&[QubitId],b:&[QubitId],cin:Option<QubitId>,cout:Option<QubitId>)->bool{
    if a.is_empty()||a.len()>b.len(){return false;}let mut target=b.to_vec();let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();rows.resize(b.len(),Vec::new());
    if let Some(q)=cout{target.push(q);rows.push(Vec::new());}
    super::phase_fit::plain_optional(c,&target,&rows,&vec![false;target.len()],cin,&mut|_,_,_|{})
}
''';p.write_bytes(raw)
# Only the already-audited pure direct square chunk entry points are adapted.
p=t/'src/point_add/width_composition.rs';raw=(square/'observer/src/point_add/width_composition.rs').read_bytes();start=raw.index(b'/// Use the original square\'s chunk boundaries')
raw=raw[:start]+b'''fn strict_square_chunk(c:&mut Builder,map:&[Vec<QubitId>],b:&[QubitId],at:usize,w:usize,prev:QubitId,out:Option<QubitId>)->bool{
    if c.current_phase()!="square"{return false;}let mut target=b[at..at+w].to_vec();let mut rows=map[at..at+w].to_vec();
    if let Some(q)=out{target.push(q);rows.push(Vec::new());}
    super::phase_fit::plain_optional(c,&target,&rows,&vec![false;target.len()],Some(prev),&mut|_,_,_|{})
}
''';p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],
 'scope':'Extend fresh phase-pebble source to exact zero-carry plain ladders with hook offsets, full plain modular ripples with zero extension, and pure square chunks. Preserve copy/deferred/known-output/known-terminal/external-carry contracts by excluding them. Original outer planners/windows/iterations retained. Baselineexact13f6; no final gate/nonce or scored result.'},indent=2)+'\n')
