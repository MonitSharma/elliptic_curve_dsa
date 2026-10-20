from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-dominance-audit-20261020';r=ex/'breakthrough-value-boolean-reset-audit-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text().replace('struct Program{inputs:','struct Program{expr:Expr,guard_exprs:Vec<u32>,inputs:').replace('struct Expr{next:u32,and:','struct Expr{nodes:Vec<(u8,u32,u32)>,implications:HashMap<(u32,u32),bool>,next:u32,and:')
s=s.replace('fn atom(&mut self)->u32{self.next+=2;self.next}','fn atom(&mut self)->u32{self.next+=2;self.nodes.push((0,0,0));self.next}')
for needle,replacement in[('let v=self.atom();self.and.insert((a,b),v);v}','let v=self.atom();*self.nodes.last_mut().unwrap()=(1,a,b);self.and.insert((a,b),v);v}'),('let v=self.atom();self.xor.insert((a,b),v);v^neg}','let v=self.atom();*self.nodes.last_mut().unwrap()=(2,a,b);self.xor.insert((a,b),v);v^neg}')]:
 assert s.count(needle)==1;s=s.replace(needle,replacement)
pos=s.index('fn compile(')
s=s[:pos]+'''impl Expr{
 fn quick_implies(&self,a:u32,b:u32,depth:usize)->bool{if a==0||b==1||a==b{return true;}if depth==0||a<=1||b==0{return false;}let an=self.nodes[(a/2-1)as usize];if an.0==1{if a&1==0{if self.quick_implies(an.1,b,depth-1)||self.quick_implies(an.2,b,depth-1){return true;}}else if self.quick_implies(an.1^1,b,depth-1)&&self.quick_implies(an.2^1,b,depth-1){return true;}}let bn=self.nodes[(b/2-1)as usize];if bn.0==1{if b&1==0{return self.quick_implies(a,bn.1,depth-1)&&self.quick_implies(a,bn.2,depth-1);}return self.quick_implies(a,bn.1^1,depth-1)||self.quick_implies(a,bn.2^1,depth-1);}false}
 fn implies(&mut self,a:u32,b:u32)->bool{if self.quick_implies(a,b,12){return true;}if let Some(&v)=self.implications.get(&(a,b)){return v;}let root=self.and(a,b^1);let answer=self.zero_truth_table(root);self.implications.insert((a,b),answer);answer}
 fn zero_truth_table(&self,root:u32)->bool{if root<=1{return root==0;}let mut pending=vec![root&!1];let mut visited=BTreeSet::new();let mut atoms=BTreeSet::new();while let Some(id)=pending.pop(){if id<=1||!visited.insert(id){continue;}if visited.len()>4096{return false;}let(k,a,b)=self.nodes[(id/2-1)as usize];if k==0{atoms.insert(id);if atoms.len()>10{return false;}}else{pending.push(a&!1);pending.push(b&!1);}}
  let ord:HashMap<_,_>=atoms.into_iter().enumerate().map(|(i,v)|(v,i)).collect();let cases=1usize<<ord.len();let words=cases.div_ceil(64);let mut table:HashMap<u32,Vec<u64>>=HashMap::new();let get=|lit:u32,table:&HashMap<u32,Vec<u64>>,j:usize|if lit<=1{if lit==1{u64::MAX}else{0}}else{let v=table[&(lit&!1)][j];if lit&1!=0{!v}else{v}};
  for id in visited{let(k,a,b)=self.nodes[(id/2-1)as usize];let mut row=vec![0;words];if k==0{let shift=ord[&id];for assignment in 0..cases{row[assignment/64]|=(((assignment>>shift)&1)as u64)<<(assignment%64);}}else{for j in 0..words{let x=get(a,&table,j);let y=get(b,&table,j);row[j]=if k==1{x&y}else{x^y};}}table.insert(id,row);}
  let last_mask=if cases<64{(1u64<<cases)-1}else{u64::MAX};(0..words).all(|j|get(root,&table,j)&if j+1==words{last_mask}else{u64::MAX}==0)
 }
}
''' +s[pos:]
needle='let mut guard_symbols:HashMap<u32,u32>=HashMap::from([(1,0)]);';assert s.count(needle)==1;s=s.replace(needle,needle+'let mut guard_exprs=vec![1u32];')
needle='guard_symbols.insert(gsymbol,id);id};';assert s.count(needle)==1;s=s.replace(needle,needle+'if g!=NO{if g as usize==guard_exprs.len(){guard_exprs.push(gsymbol);}assert!((g as usize)<guard_exprs.len());}')
s=s.replace('Program{inputs:unknown_quantum.to_vec(),nodes,guards,nq,nb,versions,rng,certified_zero_resets:certified}','Program{expr:expressions,guard_exprs,inputs:unknown_quantum.to_vec(),nodes,guards,nq,nb,versions,rng,certified_zero_resets:certified}')
start=s.index('fn normalize_resets(');end=s.index('fn optimize(',start)
s=s[:start]+'''fn normalize_resets(p:&mut Program)->usize{let mut may=vec![0u32;p.nq];for &q in &p.inputs{may[q]=1;}let mut changed=0;
 for n in &mut p.nodes{if n.k>=CINV{continue;}let t=n.t as usize;let g=p.guard_exprs[n.g as usize];if n.k==QZERO{if n.g==0||p.expr.implies(may[t],g){if n.g!=0{n.g=0;changed+=1;}may[t]=0;}else{may[t]=p.expr.and(may[t],g^1);}}else if n.k==QSWAP{let a=n.a as usize;let old_t=may[t];let old_a=may[a];let t0=p.expr.and(old_t,g^1);let t1=p.expr.and(old_a,g);let a0=p.expr.and(old_a,g^1);let a1=p.expr.and(old_t,g);may[t]=p.expr.or(t0,t1);may[a]=p.expr.or(a0,a1);}else{let mut effect=g;if matches!(n.k,QCX|QCCX){effect=p.expr.and(effect,may[n.a as usize]);}if n.k==QCCX{effect=p.expr.and(effect,may[n.b as usize]);}may[t]=p.expr.or(may[t],effect);}}
 p.certified_zero_resets+=changed;changed}
''' +s[end:]
s=s.replace('value-dominance-source-audit-20261020-v1','value-boolean-reset-source-audit-20261020-v1').replace('"abstract_audit":abstract_result,','"abstract_audit":abstract_result,"guard_boolean_nodes":p.expr.nodes.len(),"exact_implication_cache_entries":p.expr.implications.len(),')
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn union_of_possible_write_guards_is_covered_only_when_reset_guard_implies_it(){let n=u64::MAX;let ops=vec![op(K::X,n,n,3,n,0),op(K::X,n,n,3,n,1),op(K::BitStore0,n,n,n,2,n),op(K::BitStore1,n,n,n,2,0),op(K::BitStore1,n,n,n,2,1),op(K::Hmr,n,n,3,3,2),op(K::CX,n,3,2,n,n)];let p=checked(&ops,&[0,1,2],&[0,1,2]);assert!(p.nodes.iter().any(|n|n.k==QZERO&&n.g==0));let p=checked(&ops,&[0,1,2,3],&[0,1,2]);assert!(p.nodes.iter().any(|n|n.k==QZERO&&n.g!=0));}
 #[test]fn exact_guard_implication_truth_tables_and_negative_cases(){let mut e=Expr::default();let a=e.atom();let b=e.atom();let and=e.and(a,b);let or=e.or(a,b);let xor=e.xor(a,b);assert!(e.implies(and,a));assert!(e.implies(a,or));assert!(!e.implies(or,a));assert!(e.implies(a^1,and^1));assert!(e.implies(xor,or));assert!(!e.implies(or,xor));let mut many=1;for _ in 0..11{let atom=e.atom();many=e.and(many,atom);}let unrelated=e.atom();assert!(!e.implies(many,unrelated));}
''' +s[pos:]
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('15 passed; 0 failed;','17 passed; 0 failed;').replace("'native_controls':15","'native_controls':17").replace('Fifteen protected native','Seventeen protected native').replace('normalize resets after every current-IR deadwrite/cancellation round, with original arbitrary quantuminput set retained','sound necessary-nonzero Boolean unions/controlled effects and exact resetguard implication; <=10atom/4096node exhaustive truth tables, unknown unproved guards retained; original arbitrary quantuminputs retained')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Verification-only exact Boolean necessary-condition reset proof

Same frozen oldproduct61927788 andprotecteddependencies; no candidate/nonce/gate
change. Retain original arbitraryquantum/classicalinput set. Track a conservative
Boolean condition MAY under which each quantumvalue could be1: input1/helper0;
X adds guard; CX/CCX add guard AND necessaryconditions ofcontrol values; swap
propagates both oldconditions under guard/!guard. Conditionalreset restricts
MAY to!guard. A reset becomesglobalzero ONLY after proving MAY=>guard exactly.

ImmutableclassicalSSA expressions use AND/XOR/complement DAGs. Guardimplication
uses soundstructural rules orEXHAUSTIVE truth tables with<=10freeatoms and4096DAG
nodes. Larger/inconclusive cones stayUNKNOWN/unmodified; no sampled identities.
Proofresults cached only onimmutable expressionpairs. Recompute oncurrent
value-equivalent IR afterdeadwrite/involution elimination. Phase omitted; this
isNOTa quantumresource circuit oracceptancecertificate. Unknownmeasurements
never get fixed/arbitrarilyzeroed. OriginalRNGslots/CRNGdefs preserved separately.

17nativecontrols add OR-of-write-guards reset coverage, arbitrarynonoutputinput
counterexample, exactpositive/negative implication truth tables/overbudget case.
Thenfixed label value-boolean-reset-source-audit-20261020-v1,8arbitraryinitial
fixtures/24fullprotected finalvalue comparisons. No nonce screened/rejected.
Futurefilters need separateoriginalFS/curve/source/shot qualification andmay
onlyskipnonces with certifiedwrongpoint bits; fullphase/dirty/9024acceptance
remainsoriginalengine/benchmark. Priornegativeaudits kept, never scoreIRcounts.
''');print(r)
