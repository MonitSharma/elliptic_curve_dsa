"""Prepare an exact values-only guard fusion experiment, preserving all prior audits."""
from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-boolean-reset-audit-20261020';r=ex/'breakthrough-value-guard-fusion-audit-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text().replace('struct Program{expr:Expr,','struct Program{symbols:Vec<u32>,expr:Expr,').replace('Program{expr:expressions,','Program{symbols,expr:expressions,')
start=s.index('fn cancel(');end=s.index('// Recompute reset dominance',start)
s=s[:start]+'''fn fused_guard(p:&mut Program,a:u32,b:u32)->Option<u32>{
 if a==b{return None;}let common=intersect(&p.guards[a as usize],&p.guards[b as usize]);
 let mut h=1;for &v in &common{h=p.expr.and(h,p.symbols[v as usize]);}
 let x=p.expr.xor(p.guard_exprs[a as usize],p.guard_exprs[b as usize]);
 if !p.expr.implies(h,x)||!p.expr.implies(x,h){return None;}
 if let Some(i)=p.guards.iter().position(|g|*g==common){return Some(i.try_into().unwrap());}
 let id=p.guards.len().try_into().unwrap();p.guards.push(common);p.guard_exprs.push(h);Some(id)
}
fn cancel(p:&mut Program)->usize{
 let mut touch=vec![usize::MAX;p.nq];let mut write=touch.clone();let mut prior_touch=vec![[usize::MAX;3];p.nodes.len()];let mut prior_write=prior_touch.clone();let mut alive=vec![true;p.nodes.len()];let mut pending:HashMap<(u8,u32,u32,u32),usize>=HashMap::new();let mut removed=0;
 for i in 0..p.nodes.len(){let mut n=p.nodes[i];if n.k>=CINV{continue;}let qs=parts(&n);
  for &q in &qs{while touch[q]!=usize::MAX&&!alive[touch[q]]{let j=touch[q];let pos=parts(&p.nodes[j]).iter().position(|&x|x==q).unwrap();touch[q]=prior_touch[j][pos];}while write[q]!=usize::MAX&&!alive[write[q]]{let j=write[q];let pos=parts(&p.nodes[j]).iter().position(|&x|x==q).unwrap();write[q]=prior_write[j][pos];}}
  let targets=if n.k==QSWAP{vec![n.t as usize,n.a as usize]}else{vec![n.t as usize]};let controls:Vec<_>=qs.iter().copied().filter(|q|!targets.contains(q)).collect();let key=(n.k,n.a,n.b,n.t);
  if n.k<QZERO{if let Some(&j)=pending.get(&key){if alive[j]&&targets.iter().all(|&q|touch[q]==j)&&controls.iter().all(|&q|write[q]==usize::MAX||write[q]<j){
   if p.nodes[j].g==n.g{alive[j]=false;alive[i]=false;removed+=2;pending.remove(&key);continue;}
   if let Some(g)=fused_guard(p,p.nodes[j].g,n.g){alive[j]=false;removed+=1;n.g=g;p.nodes[i]=n;}
  }}pending.insert(key,i);}
  for(j,&q)in qs.iter().enumerate(){prior_touch[i][j]=touch[q];prior_write[i][j]=write[q];touch[q]=i;if targets.contains(&q){write[q]=i;}}
 }p.nodes=std::mem::take(&mut p.nodes).into_iter().zip(alive).filter_map(|(n,k)|k.then_some(n)).collect();removed}
''' +s[end:]
s=s.replace('value-boolean-reset-source-audit-20261020-v1','value-guard-fusion-source-audit-20261020-v1')
needle='assert_eq!(p.nodes.iter().filter(|n|n.k==QCX).count(),2);}'
assert s.count(needle)==1;s=s.replace(needle,'assert_eq!(p.nodes.iter().filter(|n|n.k==QCX).count(),1);assert_eq!(p.nodes.iter().find(|n|n.k==QCX).unwrap().g,0);}')
s=s.replace('fn changed_per_op_guard_prevents_false_gate_cancellation()','fn complementary_per_op_guards_fuse_to_one_gate_never_cancel_to_zero()')
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn complementary_nested_guards_fuse_only_to_captured_common_guard(){let n=u64::MAX;let ops=vec![op(K::PushCondition,n,n,n,n,0),op(K::CX,n,0,2,n,1),op(K::BitInvert,n,n,n,1,n),op(K::CX,n,0,2,n,1),op(K::PopCondition,n,n,n,n,n)];let p=checked(&ops,&[0,1,2],&[0,1,2]);let gates:Vec<_>=p.nodes.iter().filter(|n|n.k==QCX).collect();assert_eq!(gates.len(),1);assert_eq!(p.guards[gates[0].g as usize],vec![0]);}
 #[test]fn independent_guards_do_not_get_or_fused_or_cancelled(){let n=u64::MAX;let ops=vec![op(K::CX,n,0,2,n,0),op(K::CX,n,0,2,n,1)];let p=checked(&ops,&[0,1,2],&[0,1,2]);assert_eq!(p.nodes.iter().filter(|n|n.k==QCX).count(),2);}
 #[test]fn guarded_value_programs_with_mutating_controls_match_full_protected_simulator(){let n=u64::MAX;let mut seed=0xa8d7135f23649b01u64;for _ in 0..128{let mut ops=vec![];for _ in 0..80{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let t=(seed>>8)%4;let a=(t+1+(seed>>16)%3)%4;let b=(0..4).find(|&q|q!=t&&q!=a).unwrap();let guard=if seed&4!=0{n}else{(seed>>24)%2};ops.push(match seed%5{0=>op(K::X,n,n,t,n,guard),1=>op(K::CX,n,a,t,n,guard),2=>op(K::CCX,b,a,t,n,guard),3=>op(K::Swap,n,a,t,n,guard),_=>op(K::BitInvert,n,n,n,(seed>>32)%2,guard)});}checked(&ops,&[0,1,2,3],&[0,1,2,3]);}}
''' +s[pos:]
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('17 passed; 0 failed;','20 passed; 0 failed;').replace("'native_controls':17","'native_controls':20").replace('Seventeen protected native','Twenty protected native').replace('and read/write-commuting equal-guard involution cancellation','and read/write-commuting equal-guard cancellation or EXACT complementary-guard fusion to common conjunction; bounded exhaustive Boolean implication, never sampled')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Verification-only complementary-guard fusion

Same frozen oldproduct61927788 source and protected dependencies. Phase omitted;
not a quantum circuit, score, nonce filter or statistical gate. Two identical
self-inverse value gates may commute across read-only shared controls only if
neither target is touched and no control is written between them. Equal captured
SSA guards cancel. Distinct guards g,h fuse to one gate under their common SSA
conjunction c ONLY after exact proof (g XOR h) iff c, using the preceding sound
structural rules or exhaustive <=10atom/4096node truth tables. Inconclusive pairs
stay untouched. No classical version or random measurement slot changes.

Retain all prior reset/input/guard/RNG/fault controls. Strengthen the complementary
per-op guard regression to require one unconditional gate, never zero; add nested
common-guard and independent-guard counterexamples plus 128 protected exhaustive
six-input-lane value programs with mutated controls, swaps and conditional bits.
20 native tests before fixed fullsource audit, 8 arbitrary input fixtures and24
protected whole-stream value comparisons. Original registered quantum inputs
arbitrary; helpers zero. No nonce screened/rejected. Any actual future rejection
filter requires independent source/originalFS/curve/failure-witness qualification;
acceptance remains full original phase/dirty simulator and unchanged benchmark.
''')
print(r.name)
