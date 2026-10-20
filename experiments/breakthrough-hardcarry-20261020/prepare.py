"""Preserve all original1234 planners; enforce an independent carry cap."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-square-short-20261020';phase=ws/'breakthrough-phase-fusion-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not t.exists()and(old/'replay.exit').read_text().strip()=='0'and(phase/'run.exit').read_text().strip()=='0'
f=json.loads((old/'SOURCE_FREEZE.json').read_text());pf=json.loads((phase/'SOURCE_FREEZE.json').read_text())
for parent,freeze,sub in[(old,f,'observer'),(phase,pf,'primitive')]:assert all(sha(parent/sub/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
p=t/'src/point_add/phase_fusion.rs';p.write_bytes((phase/'primitive/src/point_add/phase_fusion.rs').read_bytes().replace(b'fn valid(',b'pub(super) fn valid('))
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod phase_fusion;\n')
edit('mod.rs',b'    let break_cap = std::env::var("BREAK_CAP").expect("Diagnostic BREAK_CAP required");',b'''    let break_cap = std::env::var("BREAK_CAP").expect("Diagnostic BREAK_CAP required");
    assert_eq!(break_cap,"1234","All original planners remain1234");
    let hard=std::env::var("BREAK_HARD").expect("Separate hard carry limit required");
    assert!(["1234","1233"].contains(&hard.as_str()));''')
edit('mod.rs',b'    std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);',b'    std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);\n    std::env::set_var("HARD_CARRY_CAP",&hard);')
for name in['modular.rs','width_composition.rs']:
 edit(name,b'let hard=std::env::var("HEO_PIN_PP_WALK_MAX_QUBITS")',b'let hard=std::env::var("HARD_CARRY_CAP")')
pb=(phase/'primitive/src/point_add/builder.rs').read_bytes();start=pb.index(b'    /// Three-body phase');end=pb.index(b'    pub fn cz(',start)
edit('builder.rs',b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {',pb[start:end]+b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {')
adapter=(ws/'breakthrough-parity-integration-20261020/adapter.rs').read_bytes().replace(b'    const TARGET:usize=1200;',b'    let target=hard_carry_cap();if target>=1234{return false;}').replace(b'.saturating_sub(TARGET)',b'.saturating_sub(target)')
with(t/'src/point_add/leapfrog.rs').open('ab')as stream:stream.write(b'\nfn hard_carry_cap()->usize{std::env::var("HARD_CARRY_CAP").expect("hard carry cap").parse().unwrap()}\n'+adapter)
needle=b'fn ladder_parity_add(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], cin: Option<QubitId>) {'
edit('leapfrog.rs',needle,needle+b'\n    if parity_bridge_try(c,acc,add,cin){return;}')
needle=b'fn gidney_add_lean(c: &mut Builder, a: &[QubitId], b: &[QubitId], cin: Option<QubitId>) {'
edit('leapfrog.rs',needle,needle+b'\n    if a.len()==b.len(){let terms:Vec<_>=a.iter().map(|&q|vec![q]).collect();if parity_bridge_try(c,b,&terms,cin){return;}}')
needle=b'fn carry_out_parity_xor(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], comp: bool, cin: QubitId, out: Option<QubitId>) {'
edit('leapfrog.rs',needle,needle+b'''
    if out.is_none()&&acc.len()>=2&&c.active_qubits()as usize+acc.len()-1>hard_carry_cap(){
        let start=c.op_count();if super::phase_fusion::apply(c,acc,add,comp,cin,true){eprintln!("HARD_PHASE_FUSION\\tparity\\t{start}\\t{}",c.op_count());return;}
        assert_eq!(start,c.op_count());
    }
''')
needle=b'fn lin_lt_phase(c: &mut Builder, a: &[QubitId], add: &[Lin], cin: QubitId) {'
edit('leapfrog.rs',needle,needle+b'''
    if a.len()>=2&&c.active_qubits()as usize+a.len()-1>hard_carry_cap(){
        let rows:Vec<_>=add.iter().map(|v|v.w.clone()).collect();
        if super::phase_fusion::valid(a,&rows,cin){
            let w=a.len();let start=c.op_count();c.x_all(a);let mut d=vec![cin];
            for i in 0..w-2{let q=m_carry(c,a[i],&add[i],d[i]);d.push(q);}
            assert!(super::phase_fusion::pair(c,a[w-2],a[w-1],d[w-2],&add[w-2].w,add[w-2].one,&add[w-1].w,add[w-1].one,false));
            for i in(1..w-1).rev(){m_carry_erase(c,d[i],a[i-1],&add[i-1],d[i-1]);}
            c.x_all(a);eprintln!("HARD_PHASE_FUSION\\tlin\\t{start}\\t{}",c.op_count());return;
        }
    }
''')
# Only phase-only YP8 branches. Value-producing output branches retain their ANDs.
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();flat=raw.replace(b'\r',b'')
start=flat.index(b'fn yp8_logic(');end=flat.index(b'    zlin_off(c, &tv, &bview);',start)
sub=flat[start:end];substart=sub.index(b'        None => {\n            c.x(tv[1]);');head=sub[:substart];tail=sub[substart:]
replacements=[
 (b'let r3 = and_new(c, a1, ct); // [v = 3] & added\n                c.cz(q1, r3);\n                and_erase(c, r3, a1, ct);',b'c.ccz(q1,a1,ct);'),
 (b'let r2 = and_new(c, tv[2], s1); // z2 & not flipped\n                c.cz(q1, r2);\n                and_erase(c, r2, tv[2], s1);',b'c.ccz(q1,tv[2],s1);'),
 (b'let r3 = and_new(c, a1, ct); // [v = 3] & added\n                c.cz(q1, r3);\n                and_erase(c, r3, a1, ct);',b'c.ccz(q1,a1,ct);')]
# First r3 spelling occurs in both veto branches; replace each exact occurrence once.
needle,repl=replacements[0];assert tail.count(needle)==2
tail=tail.replace(needle,b'if hard_carry_cap()<1234{'+repl+b'}else{'+needle+b'}')
needle,repl=replacements[1];assert tail.count(needle)==1
tail=tail.replace(needle,b'if hard_carry_cap()<1234{'+repl+b'}else{'+needle+b'}')
# Preserve original CR/CR/LF bytes outside this exact function-region substitution.
oldsub=sub;newsub=head+tail
lineending=b'\r\r\n'if b'\r\r\n'in raw else b'\r\n'if b'\r\n'in raw else b'\n'
encoded_old=oldsub.replace(b'\n',lineending);encoded_new=newsub.replace(b'\n',lineending)
assert raw.count(encoded_old)==1;raw=raw.replace(encoded_old,encoded_new);p.write_bytes(raw)
# Increase existing contiguous Cuccaro bridge runs only when every new pivot is unique.
needle=b'    let owned=if cout.is_some(){n-1}else{n-2};assert!(bridges<owned);'
edit('bridge.rs',needle,b'''    let owned=if cout.is_some(){n-1}else{n-2};
    let hard=std::env::var("HARD_CARRY_CAP").unwrap().parse::<usize>().unwrap();
    let need=(c.active_qubits()as usize+owned-bridges).saturating_sub(hard);
    let desired=bridges+need;
    let bridges=if need>0&&desired<owned&&(owned-desired..owned).all(|i|a.iter().filter(|&&q|q==a[i]).count()==1&&Some(a[i])!=cin){desired}else{bridges};
    assert!(bridges<owned);''')
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'all_original_planner_caps':1234,'scope':'Independent hard carry cap. Native-tested exact parity borrowing, square zero-extension, phase fusion, phase-only YP8 temporary-AND elimination via scored CCZ, unique direct bridge pivots. Original planners/windows/iterations retained. No final gate, nonce or scored result.'},indent=2)+'\n')
