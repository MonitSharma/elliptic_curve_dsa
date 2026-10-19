from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-support-tight-20261019/tight_color.rs').read_text()
needle=' for(i,original)in v.iter().enumerate(){let mut o=*original;'
assert s.count(needle)==1
s=s.replace(needle,''' let mut alias_states=0usize;let mut alias_queries=0usize;let mut alias_capped_states=0usize;let mut alias_first_uncovered=None;let mut alias_examples=vec![];let mut probe_bounds=Bounds{cuts:0};
'''+needle)
needle='  if i%1_000_000==0'
assert s.count(needle)==1
s=s.replace(needle,'''  if alias_states<256&&alias_first_uncovered.is_none()&&nq-free.len()==nq{
   assert!(q.iter().all(|x|!x.is_no()));alias_states+=1;let conditional:Vec<_>=(0..nq).filter(|&q0|!q[q0].is_yes()).collect();let mut found=None;let mut tried=0usize;let mut capped=false;
   'pairs:for a in 0..conditional.len(){for b in a+1..conditional.len(){if tried>=32768{capped=true;break 'pairs;}tried+=1;let x=conditional[a];let y=conditional[b];if probe_bounds.and(&q[x],&q[y],&d).is_no(){found=Some((x,y));break 'pairs;}}}
   alias_queries+=tried;if capped{alias_capped_states+=1;}if alias_examples.len()<16{alias_examples.push(serde_json::json!({"op":i,"conditional_roles":conditional.len(),"pairs_examined":tried,"certified_pair":found,"capped":capped}));}
   if !capped&&found.is_none(){alias_first_uncovered=Some(serde_json::json!({"op":i,"conditional_roles":conditional,"universal_support_roles":q.iter().filter(|x|x.is_yes()).count(),"pairs_examined":tried,"reason":"No pair certified disjoint by unchanged strong support bounds; not a physical-width lower bound."}));}
  }
'''+needle)
needle='"status":"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE",'
assert s.count(needle)==1
s=s.replace(needle,needle+'''"branch_alias_probe":{"status":"READ_ONLY_DISJOINT_SUPPORT_DIAGNOSTIC_NOT_A_SCORE","states_examined":alias_states,"pair_queries":alias_queries,"pair_cap":32768,"state_cap":256,"capped_states":alias_capped_states,"diagnostic_support_cuts":probe_bounds.cuts,"first_uncertified_full_width_state":alias_first_uncovered,"examples":alias_examples},''')
(r/'alias_probe.rs').write_text(s,encoding='utf-8',newline='\n')
