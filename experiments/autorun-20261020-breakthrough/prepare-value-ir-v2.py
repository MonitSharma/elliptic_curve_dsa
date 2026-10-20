from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-value-ir-audit-20261020';r=a.parent/'breakthrough-value-ir-audit-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text()
start=s.index('fn cancel(');end=s.index('fn optimize(',start)
s=s[:start]+'''fn cancel(p:&mut Program)->usize{
 let mut touch=vec![usize::MAX;p.nq];let mut write=touch.clone();let mut prior_touch=vec![[usize::MAX;3];p.nodes.len()];let mut prior_write=prior_touch.clone();let mut alive=vec![true;p.nodes.len()];let mut pending:HashMap<(u8,u32,u32,u32,u32),usize>=HashMap::new();let mut removed=0;
 for(i,n)in p.nodes.iter().enumerate(){if n.k>=CINV{continue;}let qs=parts(n);
  for &q in &qs{while touch[q]!=usize::MAX&&!alive[touch[q]]{let j=touch[q];let pos=parts(&p.nodes[j]).iter().position(|&x|x==q).unwrap();touch[q]=prior_touch[j][pos];}while write[q]!=usize::MAX&&!alive[write[q]]{let j=write[q];let pos=parts(&p.nodes[j]).iter().position(|&x|x==q).unwrap();write[q]=prior_write[j][pos];}}
  let targets=if n.k==QSWAP{vec![n.t as usize,n.a as usize]}else{vec![n.t as usize]};let controls:Vec<_>=qs.iter().copied().filter(|q|!targets.contains(q)).collect();let key=(n.k,n.a,n.b,n.t,n.g);
  if n.k<QZERO{if let Some(&j)=pending.get(&key){if alive[j]&&targets.iter().all(|&q|touch[q]==j)&&controls.iter().all(|&q|write[q]==usize::MAX||write[q]<j){alive[j]=false;alive[i]=false;removed+=2;pending.remove(&key);continue;}}pending.insert(key,i);}
  for(j,&q)in qs.iter().enumerate(){prior_touch[i][j]=touch[q];prior_write[i][j]=write[q];touch[q]=i;if targets.contains(&q){write[q]=i;}}
 }p.nodes=std::mem::take(&mut p.nodes).into_iter().zip(alive).filter_map(|(n,k)|k.then_some(n)).collect();removed}
''' + s[end:]
s=s.replace('for _ in 0..32{','for _ in 0..2048{').replace('untouched-participant/equal-guard','read/write-commuting equal-guard')
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn shared_read_only_control_commutes_but_target_reads_and_control_writes_block(){let n=u64::MAX;let ops=vec![op(K::CX,n,0,2,n,n),op(K::CX,n,0,1,n,n),op(K::CX,n,0,2,n,n),op(K::CX,n,2,1,n,n),op(K::CX,n,0,2,n,n),op(K::X,n,n,0,n,n),op(K::CX,n,0,2,n,n)];let mut p=compile(&ops,&[0,1,2]);assert_eq!(cancel(&mut p),2);checked(&ops,&[0,1,2],&[0,1,2]);}
''' +s[pos:]
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('7 passed; 0 failed;','8 passed; 0 failed;').replace("'native_controls':7","'native_controls':8").replace('Seven protected native','Eight protected native').replace('untouched-participant equal-guard involution cancellation','read/write-commuting equal-guard involution cancellation; fixedpoint or2048round bound')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text((old/'PLAN.md').read_text()+'''\nV2 independently freezes new verification tool: up to2048 rounds and exact\nread/write commutation. Identical guarded involutions may cancel across gates\nthat only read their common controls; every target must have no intervening\nread/write, and controls no intervening write. Linked prior-touch/prior-write\nrecords skip cancelled nodes. Eighth protected exhaustive native control covers\nshared read-only controls, target reads and control writes. No nonce rejection\nor quantum candidate/resource score. Prior32-round audit stays unchanged.\n''')
print(r)
