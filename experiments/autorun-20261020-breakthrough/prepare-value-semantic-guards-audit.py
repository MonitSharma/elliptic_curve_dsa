from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-curve-audit-v2-20261020';r=ex/'breakthrough-value-semantic-guards-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore','verify-input.py']:shutil.copyfile(old/n,r/n)
for n in ['Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();needle='#[derive(Default)]struct Expr{';assert s.count(needle)==1;s=s.replace(needle,(a/'value-semantic-guards.rs').read_text()+'\n'+needle+'truths:Vec<SemTruth>,canonical:HashMap<SemTruth,u32>,')
needle='fn atom(&mut self)->u32{self.next+=2;self.nodes.push((0,0,0));self.next}';assert s.count(needle)==1;s=s.replace(needle,'fn atom(&mut self)->u32{self.next+=2;self.nodes.push((0,0,0));let t=SemTruth{atoms:vec![self.next],table:2};self.truths.push(t.clone());self.canonical.insert(t,self.next);self.next}')
for k,field,tail in [(1,'and','v}'),(2,'xor','v^neg}')]:
 needle=f'let v=self.atom();*self.nodes.last_mut().unwrap()=({k},a,b);self.{field}.insert((a,b),v);{tail}';replacement=f'let v=self.semantic_node({k},a,b);self.{field}.insert((a,b),v);{tail}';assert s.count(needle)==1;s=s.replace(needle,replacement)
pos=s.rfind('\n}');s=s[:pos]+'''
 #[test]fn semantic_guards_canonicalize_distributivity_and_remove_unused_atoms(){let mut e=Expr::default();let a=e.atom();let b=e.atom();let ab=e.and(a,b);let anb=e.and(a,b^1);let distributed=e.xor(ab,anb);assert_eq!(distributed,a);let or=e.or(a,b);let left=e.and(or,a);assert_eq!(left,a);assert_ne!(or,a);}
 #[test]fn semantic_guard_keys_match_all_original_six_atom_assignments(){fn value(e:&Expr,v:u32,assignment:usize,atoms:&[u32])->bool{if v<=1{return v==1;}let(k,a,b)=e.nodes[(v/2-1)as usize];let x=if k==0{let bit=atoms.iter().position(|&x|x==v&!1).expect("original atom");assignment>>bit&1!=0}else if k==1{value(e,a,assignment,atoms)&&value(e,b,assignment,atoms)}else{value(e,a,assignment,atoms)^value(e,b,assignment,atoms)};x^(v&1!=0)}let mut e=Expr::default();let atoms:Vec<_>=(0..6).map(|_|e.atom()).collect();let mut pool=atoms.clone();let mut seed=0xa8d7135f23649b01u64;for _ in 0..500{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let a=pool[(seed as usize)%pool.len()];let b=pool[((seed>>17)as usize)%pool.len()];let g=pool[((seed>>33)as usize)%pool.len()];let kind=seed%4;let result=match kind{0=>e.and(a,b),1=>e.xor(a,b),2=>e.or(a,b),_=>e.ite(g,a,b)};for assignment in 0..64{let av=value(&e,a,assignment,&atoms);let bv=value(&e,b,assignment,&atoms);let gv=value(&e,g,assignment,&atoms);let expected=match kind{0=>av&bv,1=>av^bv,2=>av|bv,_=>if gv{av}else{bv}};assert_eq!(value(&e,result,assignment,&atoms),expected);}if pool.len()<64{pool.push(result);}else{pool[((seed>>8)as usize)%64]=result;}}}
 #[test]fn distributed_classical_guard_allows_only_proved_quantum_value_cancellation(){let n=u64::MAX;let ops=vec![op(K::BitStore0,n,n,n,2,n),op(K::BitStore1,n,n,n,2,0),op(K::BitStore0,n,n,n,3,n),op(K::BitStore1,n,n,n,3,1),op(K::BitStore0,n,n,n,4,n),op(K::PushCondition,n,n,n,n,2),op(K::BitStore1,n,n,n,4,3),op(K::PopCondition,n,n,n,n,n),op(K::BitInvert,n,n,n,3,n),op(K::BitStore0,n,n,n,5,n),op(K::PushCondition,n,n,n,n,2),op(K::BitStore1,n,n,n,5,3),op(K::PopCondition,n,n,n,n,n),op(K::BitStore0,n,n,n,6,n),op(K::BitInvert,n,n,n,6,4),op(K::BitInvert,n,n,n,6,5),op(K::X,n,n,2,n,6),op(K::X,n,n,2,n,0)];let p=checked_known_bits(&ops,&[0,1]);assert_eq!(p.nodes.iter().filter(|n|n.k==QX).count(),0);}
''' +s[pos:];(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('value_curve_audit','value_semantic_guards_audit'))
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},native_controls=24,scope='Exact six-free-atom classical truth canonicalization with unused-atom elimination/complement keys and immutable SSA aliases. Above support bound stays opaque, never sampled. Frozen old6192 quantum source unchanged. Reuse32validcurve verification fixtures to compare proof precision; no gate/circuit/nonce tuning or rejection.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name).replace('value_curve_audit','value_semantic_guards_audit').replace('21 passed; 0 failed;','24 passed; 0 failed;');(r/n).write_bytes(s.encode())
(r/'PLAN.md').write_text('''# Exact semantic classical guard canonicalization

Prior aliases only hash-cons AND/XOR syntax. Compute exact truth tables for<=6
free immutable classical/opaque atoms, eliminate unused variables, normalize
complements and intern by FULL support/table equality. Larger expressions remain
opaque symbols for their actual immutable functions; independent-atom widening
can only miss identities, never invent one. Preserve raw expression DAGs for
existing implication proofs; source/RNG slots unchanged. No sampled equality.

Retain21native controls, add distributivity/unused-support identity, complete64
assignments of6atoms over500expressions, and protected quantumvalue cancellation
from distributed equivalent classical guards (24total). Then same frozen6192,
8arbitrary/32validcurve verifier fixtures,120fullprotected value comparisons.
Fixture reuse evaluates verifier precision only; no circuit/table/cut tuning,
gate verdict resampling, nonce screening or quantumresource claim. Finalgate
and originalFS qualification still mandatory before any future production.
''');print(r.name)
