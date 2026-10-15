// Lazy construction of a sole AND used only under classical guards.
// Every original measurement stays in place. The measured erase's exact
// CZ twin is suppressed exactly when no read caused the AND to be built.
pub fn lazy_single(ops:Vec<Op>)->Vec<Op>{
 let l:Vec<L>=ops.iter().map(to_l).collect();drop(ops);
 let a=analyze(&l);let mut ed=Edits::new();let mut nb=max_bit(&l);
 let wanted:HashSet<_>=a.contribs.iter().filter(|c|c.end_kind==E_HMR).map(|c|c.end_bit).collect();
 let mut outcome_uses:HashMap<u32,Vec<u32>>=HashMap::new();
 for(j,o)in l.iter().enumerate(){if matches!(o.kind,K_PUSH|K_POP|K_BS0|K_BS1|K_BINV){continue;}for &b in &a.cx.sets[a.opctx[j] as usize]{if wanted.contains(&b){outcome_uses.entry(b).or_default().push(j as u32);}}}
 // Analysis.contribs.reads is deliberately phase-only; gather every physical
 // data/phase read for this distinct pass instead of reusing that field.
 let mut physical_reads:HashMap<u32,Vec<(u32,u32)>>=HashMap::new();
 for(j,o)in l.iter().enumerate(){
  let qs=match o.kind {K_CCX=>[o.c1,o.c2,NQ],K_CX=>[o.c1,NQ,NQ],K_Z=>[o.t,NQ,NQ],K_CZ=>[o.c1,o.t,NQ],K_CCZ=>[o.c1,o.c2,o.t],_=>[NQ;3]};
  for q in qs{if q!=NQ{physical_reads.entry(q).or_default().push((j as u32,a.opctx[j]));}}
 }
 // Accepted target lifetimes and new temporary reads prevent cross-site interference.
 let mut kept:Vec<(u32,u32,u32,Vec<(u32,u32)>)>=vec![];
 let mut selected=0;
 for c in &a.contribs {
  if c.ctx!=0 || c.swapped || c.end_kind!=E_HMR || !c.end_sole {continue;}
  let p=c.op as usize;let e=c.end_op as usize;let original=l[p];
  if original.cc!=NQ || l[e].cc!=NQ || a.opctx[e]!=0 || a.bderived[c.end_bit as usize] || ed.touched(c.op){continue;}
  let Some(all_reads)=physical_reads.get(&c.wire) else{continue;};
  let rs=all_reads.partition_point(|r|r.0<=c.op);let re=all_reads.partition_point(|r|r.0<c.end_op);let these_reads=&all_reads[rs..re];
  if these_reads.is_empty()||these_reads.iter().any(|&(_,ctx)|a.cx.sets[ctx as usize].is_empty()){continue;}
  if (p+1..e).any(|j|{let o=l[j];o.t==c.wire&&matches!(o.kind,K_X|K_CX|K_CCX|K_R|K_HMR|K_SWAP)||o.kind==K_SWAP&&o.c1==c.wire}){continue;}
  let Some(fixes)=a.fixcz.get(&c.end_bit) else{continue;};
  let matches:Vec<_>=fixes.iter().filter(|&&(j,x,y)|((x==c.va&&y==c.vb)||(x==c.vb&&y==c.va))&&a.cx.sets[a.opctx[j as usize] as usize]==vec![c.end_bit]).collect();
  if matches.len()!=1{continue;}let fix=matches[0].0;
  // The outcome may control only its one exact CZ twin, never data operations.
  if outcome_uses.get(&c.end_bit).is_none_or(|v|v.as_slice()!=[fix]){continue;}
  if ed.touched(fix){continue;}
  let mut reads:Vec<usize>=these_reads.iter().map(|r|r.0 as usize).collect();reads.sort_unstable();reads.dedup();
  if reads.iter().any(|&j|j<=p||j>=e){continue;}
  let Some(forms)=forms_at(&l,&a,p,&[original.c1,original.c2],&reads) else{continue;};
  let mut blocks=vec![];let mut uses=vec![];let mut bad=false;
  for (i,&at) in reads.iter().enumerate(){
   let(fa,fb)=(&forms[i][0],&forms[i][1]);
   if fa.0.is_empty()||fb.0.is_empty()||fa.0.contains(&c.wire)||fb.0.contains(&c.wire){bad=true;break;}
   let ha=*fa.0.iter().find(|w|!fb.0.contains(w)).unwrap_or(&fa.0[0]);
   let mut fbc=fb.0.clone();let mut fbk=fb.1;
   if fb.0.contains(&ha){for &w in fa.0.iter().filter(|&&w|w!=ha){if let Some(j)=fbc.iter().position(|&v|v==w){fbc.swap_remove(j);}else{fbc.push(w);}}fbk^=fa.1;}
   let Some(&hb)=fbc.iter().find(|&&w|w!=ha) else{bad=true;break;};
   let mut on=vec![];
   for &w in fa.0.iter().filter(|&&w|w!=ha){on.push(op(K_CX,w,ha,NQ));}if fa.1{on.push(op(K_X,NQ,ha,NQ));}
   for &w in fbc.iter().filter(|&&w|w!=hb){on.push(op(K_CX,w,hb,NQ));}if fbk{on.push(op(K_X,NQ,hb,NQ));}
   for &w in fa.0.iter().chain(fb.0.iter()){uses.push((w,at as u32));}
   blocks.push((at as u32,on,ha,hb));
  }
  if bad{continue;}
  if uses.iter().any(|&(w,t)|kept.iter().any(|&(q,s,z,_)|w==q&&s<t&&t<=z)) || kept.iter().any(|(_,_,_,u)|u.iter().any(|&(w,t)|w==c.wire&&c.op<t&&t<=fix)){continue;}
  let valid=nb;let temporary=nb+1;nb+=2;
  let store=|b:u32,one:bool|L{kind:if one{K_BS1}else{K_BS0},c2:NQ,c1:NQ,t:NQ,ct:b,cc:NQ,rt:NQ};
  let push=|b:u32|L{kind:K_PUSH,c2:NQ,c1:NQ,t:NQ,ct:NQ,cc:b,rt:NQ};
  let pop=L{kind:K_POP,c2:NQ,c1:NQ,t:NQ,ct:NQ,cc:NQ,rt:NQ};
  ed.replace.insert(c.op,vec![store(valid,false),store(temporary,false)]);
  for(at,on,ha,hb)in blocks {
   let mut block=vec![store(temporary,true),L{kind:K_BINV,c2:NQ,c1:NQ,t:NQ,ct:temporary,cc:valid,rt:NQ},push(temporary)];
   if l[at as usize].cc!=NQ{block.push(push(l[at as usize].cc));}
   block.extend(on.iter().copied());block.push(L{kind:K_CCX,c2:hb,c1:ha,t:c.wire,ct:NQ,cc:NQ,rt:NQ});block.extend(on.iter().rev().copied());block.push(store(valid,true));
   if l[at as usize].cc!=NQ{block.push(pop);}
   block.push(pop);block.push(store(temporary,false));
   ed.before.entry(at).or_default().extend(block);
  }
  ed.replace.insert(fix,vec![push(valid),l[fix as usize],pop]);
  let mut clear=fix as usize;while clear<l.len()&&a.depth_after[clear]!=0{clear+=1;}
  assert!(clear<l.len());ed.after.entry(clear as u32).or_default().extend([store(valid,false),store(temporary,false)]);
  kept.push((c.wire,c.op,fix,uses));selected+=1;
  println!("LAZY_SINGLE_SITE producer={} end={} fix={fix} wire={} reads={reads:?}",c.op,c.end_op,c.wire);
 }
 println!("LAZY_SINGLE_SUMMARY selected={selected} new_classical_bits={} quantum_width_unchanged=true",nb-max_bit(&l));
 ed.apply(&l).iter().map(from_l).collect()
}
