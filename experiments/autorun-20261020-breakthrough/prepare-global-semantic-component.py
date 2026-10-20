from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-global-phase-component-v2-20261020';r=ex/'breakthrough-global-semantic-component-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
qualified=(ex/'breakthrough-value-cofactor-qualification-20261020/local-tool/audit.rs').read_text()
core=qualified[qualified.index('// Exact semantic keys'):qualified.index('fn compile(')]
base=(old/'local-tool/discover.rs').read_text();start=base.index('// Full-prefix exact Boolean replay.');body=base[start:]
body=body.replace('Algebra {max_products,forgotten_products:0,next:1,products:HashMap::new(),cap,truncations:0}','Algebra {inner:Expr::default()}')
body=body.replace('let one=vec![0];let zero=vec![];','let one=1;let zero=0;').replace('!v.is_empty()','*v!=0').replace('flip.is_empty()','flip==0').replace('phase.is_empty()','phase==0').replace('!c[ct].is_empty()','c[ct]!=0')
body=body.replace('Algebra::xor_raw(&q[control],&one)','q[control]^1')
body=body.replace('alg.products.len()','alg.inner.nodes.len()').replace('alg.truncations','0usize').replace('alg.forgotten_products','0usize')
body=body.replace('assert!(s["forgotten_product_keys"].as_u64().unwrap()>0);','assert!(s["exact_product_keys"].as_u64().unwrap()>0);')
head='''mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId};
use std::collections::{HashMap,HashSet,BTreeSet};
use sha3::{Digest,Sha3_256};
type E=u32;
'''+core+'''
struct Algebra{inner:Expr}
impl Algebra{fn fresh(&mut self)->E{self.inner.atom()}fn and(&mut self,a:&E,b:&E)->E{self.inner.and(*a,*b)}fn xor(&mut self,a:&E,b:&E)->E{self.inner.xor(*a,*b)}fn select(&mut self,old:&E,new:&E,cond:&E)->E{self.inner.ite(*cond,*new,*old)}}
fn initial_inputs(ops:&[Op],nq:usize,nb:usize,alg:&mut Algebra)->(Vec<E>,Vec<E>){let no=u64::MAX;let(mut q,mut c)=(vec![0;nq],vec![0;nb]);let(mut qs,mut cs)=(HashSet::new(),HashSet::new());for o in ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no&&qs.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();}if o.c_target.0!=no&&cs.insert(o.c_target.0){c[o.c_target.0 as usize]=alg.fresh();}}}(q,c)}
'''
head+=base[base.index('fn hash('):base.index('fn initial_inputs(')]
tests=r'''
#[cfg(test)]mod semantic_algebra_controls{use super::*;
 #[test]fn distributivity_and_unused_support_are_exact(){let mut e=Expr::default();let a=e.atom();let b=e.atom();let ab=e.and(a,b);let anb=e.and(a,b^1);assert_eq!(e.xor(ab,anb),a);let or=e.or(a,b);assert_eq!(e.and(or,a),a);assert_ne!(or,a);}
 #[test]fn above_six_atom_cofactor_has_disabled_negative_control(){fn run(enabled:bool)->(u32,u32){let mut e=Expr::default();e.restricting=!enabled;let mut g=1;let mut old=1;for _ in 0..6{let a=e.atom();g=e.and(g,a);let b=e.atom();old=e.and(old,b);}assert_eq!(e.semantic(g).atoms.len(),6);assert_eq!(e.semantic(old).atoms.len(),6);let r=e.atom();let v=e.ite(g,r,old);let actual=e.and(g,v);let expected=e.and(g,r);(actual,expected)}let no=run(false);assert_ne!(no.0,no.1);let yes=run(true);assert_eq!(yes.0,yes.1);}
 #[test]fn complete_six_atom_expression_truths_match_original_functions(){fn get(e:&Expr,v:u32,assignment:usize,atoms:&[u32])->bool{if v<=1{return v==1;}let(k,a,b)=e.nodes[(v/2-1)as usize];let value=match k{0=>assignment>>atoms.iter().position(|&a|a==v&!1).unwrap()&1!=0,1=>get(e,a,assignment,atoms)&get(e,b,assignment,atoms),_=>get(e,a,assignment,atoms)^get(e,b,assignment,atoms)};value^(v&1!=0)}let mut e=Expr::default();let atoms:Vec<_>=(0..6).map(|_|e.atom()).collect();let mut pool=atoms.clone();let mut seed=0xa8d7135f23649b01u64;for _ in 0..500{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let(a,b,g)=(pool[seed as usize%pool.len()],pool[(seed>>17)as usize%pool.len()],pool[(seed>>33)as usize%pool.len()]);let kind=seed%3;let v=match kind{0=>e.and(a,b),1=>e.xor(a,b),_=>e.ite(g,a,b)};for assignment in 0..64{let(a,b,g)=(get(&e,a,assignment,&atoms),get(&e,b,assignment,&atoms),get(&e,g,assignment,&atoms));let want=match kind{0=>a&b,1=>a^b,_=>if g{a}else{b}};assert_eq!(get(&e,v,assignment,&atoms),want);}pool.push(v);if pool.len()>64{pool.remove(6);}}}
}
'''
s=head+body+tests;(t/'discover.rs').write_text(s);(r/'discover.rs').write_text(s);(r/'qualified-expression-core.rs').write_text(core)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(tool_source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},native_controls=12,scope='Full-prefix exact semantic six-atom truth canonicalization and six-depth Shannon cofactoring using unchanged qualified expression core; arbitrary initial inputs and measurement outcomes. Native9 complete-state/phase/guard controls plus3 algebra truth/cofactor-negative controls. Source fixed before stream replay, no packet/nonce/gate/score. Legacy diagnostic product-key field denotes Boolean nodes; no forgotten products or truncations.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run.py','run-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name).replace("'native_controls':18","'native_controls':12").replace('18 passed; 0 failed;','12 passed; 0 failed;');(r/n).write_bytes(s.encode())
(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
(r/'PLAN.md').write_text('''# Full-prefix semantic phase and action simplification

Replace wide XOR-vector product atoms with the already qualified exact
semantic six-atom truth canonicalizer and bounded Shannon cofactoring. The
expression core is copied byte-for-byte from the native26-qualified verifier,
used here for quantum/classical action equalities including absolute phase.
No weakening or sampled identities. Native9 full protected phase/value/guard/
RNG controls plus3 exact algebra controls, then both current parent streams.
Local5GiB/900s each, preserve any budget failure. No packet/circuit tuning,
finalgate, nonce screening or score; any useful result needs full pipeline.
''');print(r.name)
