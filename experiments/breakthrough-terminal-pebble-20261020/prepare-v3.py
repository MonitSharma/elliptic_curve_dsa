import hashlib,json,subprocess,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text())
assert(r/'run-v2.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
for name in['phase_pebble.rs','terminal_pebble.rs','modular.rs']:shutil.copyfile(t/'src/point_add'/name,r/('passing-v2-'+name))
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
needle=b'    run(c,acc,rows,ones,cin,drops,false,&mut|_,_,_|{},None,Some(desired))'
edit('phase_pebble.rs',needle,b'    known_top_with_hook(c,acc,rows,ones,cin,drops,desired,&mut|_,_,_|{})')
with(t/'src/point_add/phase_pebble.rs').open('ab')as out:out.write(b'''
pub(super) fn known_top_with_hook(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize],desired:bool,hook:&mut dyn FnMut(&mut Builder,usize,QubitId))->bool{
 run(c,acc,rows,ones,cin,drops,false,hook,None,Some(desired))
}
''')
needle=b'pub(super) fn apply(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:Option<QubitId>,drops:&[usize],desired:bool)->bool{'
edit('terminal_pebble.rs',needle,needle+b'\n apply_with_hook(c,acc,rows,ones,cin,drops,desired,&mut|_,_,_|{})\n}\npub(super) fn apply_with_hook(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:Option<QubitId>,drops:&[usize],desired:bool,hook:&mut dyn FnMut(&mut Builder,usize,QubitId))->bool{')
edit('terminal_pebble.rs',b'return super::phase_pebble::known_top(c,acc,rows,ones,ci,drops,desired);',b'return super::phase_pebble::known_top_with_hook(c,acc,rows,ones,ci,drops,desired,hook);')
edit('terminal_pebble.rs',b'let carry=c.alloc_qubit();c.ccx(q,acc[0],carry);',b'let carry=c.alloc_qubit();c.ccx(q,acc[0],carry);hook(c,1,carry);')
edit('terminal_pebble.rs',b'super::phase_pebble::known_top(c,&acc[1..],&rows[1..],&ones[1..],carry,drops,desired)',b'super::phase_pebble::known_top_with_hook(c,&acc[1..],&rows[1..],&ones[1..],carry,drops,desired,&mut|c,i,q|hook(c,i+1,q))')
# Extend the existing direct-original oracle, rather than replacing it.
edit('modular.rs',b'fn circuit(n:usize,k:usize,has_cin:bool,desired:bool,drops:Option<&[usize]>)->(Vec<Op>,Vec<QubitId>,u32){',b'''fn circuit(n:usize,k:usize,has_cin:bool,desired:bool,drops:Option<&[usize]>)->(Vec<Op>,Vec<QubitId>,u32){circuit_phase(n,k,has_cin,desired,drops,None)}
 fn circuit_phase(n:usize,k:usize,has_cin:bool,desired:bool,drops:Option<&[usize]>,phase_at:Option<usize>)->(Vec<Op>,Vec<QubitId>,u32){''')
edit('modular.rs',b'let guard=c.alloc_bit();assert_eq!(guard.0,0);',b'let guard=c.alloc_bit();assert_eq!(guard.0,0);let phase=phase_at.map(|_|c.alloc_bit());')
edit('modular.rs',b'crate::point_add::terminal_pebble::apply(c,&b,&rows,&vec![false;n],has_cin.then_some(ci),ds,desired)',b'crate::point_add::terminal_pebble::apply_with_hook(c,&b,&rows,&vec![false;n],has_cin.then_some(ci),ds,desired,&mut|c,i,q|if phase_at==Some(i-1){c.z_if(q,phase.unwrap());c.free_bit(phase.unwrap());})')
edit('modular.rs',b'Carry0::Full,Carry1::Full,None,None,Some(desired),None);',b'Carry0::Full,Carry1::Full,phase_at.map(|i|(i,phase.unwrap())),None,Some(desired),None);')
needle=b'fn fixture(n:usize,k:usize,has_cin:bool,desired:bool,drops:&[usize],guard:u64,probe:Option<usize>){'
edit('modular.rs',needle,needle+b'fixture_phase(n,k,has_cin,desired,drops,guard,probe,None);}\n fn fixture_phase(n:usize,k:usize,has_cin:bool,desired:bool,drops:&[usize],guard:u64,probe:Option<usize>,phase_at:Option<usize>){')
edit('modular.rs',b'let(old,interface,_)=circuit(n,k,has_cin,desired,None);let(new,interface2,_)=circuit(n,k,has_cin,desired,Some(drops));',b'let(old,interface,_)=circuit_phase(n,k,has_cin,desired,None,phase_at);let(new,interface2,_)=circuit_phase(n,k,has_cin,desired,Some(drops),phase_at);')
edit('modular.rs',b'a.bits[0]=guard;b.bits[0]=guard;',b'a.bits[0]=guard;b.bits[0]=guard;if phase_at.is_some(){a.bits[1]=0xD3C578A906BFE214;b.bits[1]=0xD3C578A906BFE214;}')
with(t/'src/point_add/modular.rs').open('ab')as out:out.write(b'''
#[cfg(test)]mod terminal_birth_phase_tests{
 #[test]fn original_deferred_phases_match_true_carry_birth_hooks_including_dropped_carries(){
  for has_cin in[false,true]{for desired in[false,true]{for k in[1,4,6]{for ds in[vec![],vec![1]]{for at in 0..4{super::terminal_contract_tests::fixture_phase(6,k,has_cin,desired,&ds,0xA9563C78F012DE4B,None,Some(at));}}}}}
 }
}
''')
# Sibling regression module needs this one test helper only.
edit('modular.rs',b' fn fixture_phase(n:usize',b' pub(super) fn fixture_phase(n:usize')
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v3.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V3 adds true arithmetic carry birth phase hook, including bottom zero-carry offset. Original deferred-phase oracle compares all carry positions, including early dropped carries. Needed to preserve modular square DSQ_APPLY global repair when integrating. No output/data consumer hook or unproved contract weakening.'
(r/'SOURCE_FREEZE-v3.json').write_text(json.dumps(f,indent=2)+'\n')
