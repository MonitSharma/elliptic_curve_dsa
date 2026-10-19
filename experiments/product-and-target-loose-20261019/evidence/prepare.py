"""Derive a separate noncontiguous-query experiment; keep strict v1 immutable."""
from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-and-target-20261019/and_target.rs').read_text()
s=s.replace('BTreeSet,HashSet','BTreeSet,HashSet,HashMap')
s=s.replace('targets:Vec<u64>}','targets:Vec<u64>,queries:Vec<usize>}')
start=s.index(' let mut zero=vec![true;nq]')
end=s.index('\nfn emit(',start)
s=s[:start]+''' let qubits=|o:&Op|[o.q_control1.0,o.q_control2.0,o.q_target.0];
 let mut touches:Vec<Vec<usize>>=vec![vec![];nq];let mut writes:Vec<Vec<usize>>=vec![vec![];nq];
 for(i,o)in v.iter().enumerate(){for q in qubits(o){if q!=NO{touches[q as usize].push(i);}}if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap){writes[o.q_target.0 as usize].push(i);if o.kind==K::Swap{writes[o.q_control1.0 as usize].push(i);}}}
 let mut zero=vec![true;nq];for &q in &pinned{zero[q as usize]=false;}let mut found=vec![];
 for(i,o)in v.iter().enumerate(){
  if o.kind==K::CCX&&depths[i]==0&&o.c_condition.0==NO&&zero[o.q_target.0 as usize]&&!pinned.contains(&o.q_target.0){
   let(a,b,t)=(o.q_control1.0,o.q_control2.0,o.q_target.0);let ts=&touches[t as usize];let lo=ts.partition_point(|&j|j<=i);let mut h=None;let mut targets=BTreeSet::new();let mut queries=vec![];
   for &j in &ts[lo..]{let q=&v[j];if q.kind==K::Hmr{h=Some(j);break;}if q.kind!=K::CX||q.q_control1.0!=t||q.c_condition.0!=NO||depths[j]!=0||[a,b,t].contains(&q.q_target.0){break;}if !targets.remove(&q.q_target.0){targets.insert(q.q_target.0);}queries.push(j);}
   if let Some(end)=h{if !queries.is_empty(){if let Some(z)=v.get(end+1){let hh=&v[end];let bit=hh.c_target.0;
    let stable=[a,b].iter().all(|&q|{let ws=&writes[q as usize];ws.get(ws.partition_point(|&j|j<=i)).map_or(true,|&j|j>=end)});
    let all_targets:BTreeSet<_>=queries.iter().map(|&j|v[j].q_target.0).collect();
    let isolated=all_targets.iter().all(|&q|{let ts=&touches[q as usize];let lo=ts.partition_point(|&j|j<=i);let hi=ts.partition_point(|&j|j<end);ts[lo..hi].iter().all(|j|queries.binary_search(j).is_ok())});
    if stable&&isolated&&depths[end]==0&&hh.q_target.0==t&&hh.c_condition.0==NO&&z.kind==K::CZ&&z.c_condition.0==bit&&((z.q_control1.0==a&&z.q_target.0==b)||(z.q_control1.0==b&&z.q_target.0==a))&&hmr_safe.contains(&end)&&!pinned_b.contains(&bit){found.push(Site{start:i,end:end+2,mr:end,a,b,t,bit,targets:targets.into_iter().collect(),queries});}
   }}}
  }
  if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap)&&o.q_target.0!=NO{zero[o.q_target.0 as usize]=matches!(o.kind,K::R|K::Hmr)&&depths[i]==0&&o.c_condition.0==NO;if o.kind==K::Swap{zero[o.q_control1.0 as usize]=false;}}
 }found
}
''' + s[end:]
start=s.index('let sites=discover(&v);let mut out=')
end=s.index('\n let mut event_map=',start)
s=s[:start]+'''let sites=discover(&v);let mut out=Vec::with_capacity(v.len());let mut removed=HashSet::new();let mut edits=HashMap::new();let mut deleted=HashSet::new();let mut rows=vec![];
 for s in &sites{assert!(edits.insert(s.start,emit(s)).is_none());for j in s.queries.iter().copied().chain([s.mr,s.mr+1]){assert!(deleted.insert(j),"overlapping edited instruction");}removed.insert(s.mr);rows.push(serde_json::json!({"start":s.start,"end_exclusive":s.end,"removed_Hmr":s.mr,"removed_bit":s.bit,"a":s.a,"b":s.b,"temporary":s.t,"targets":s.targets,"query_indices":s.queries}));}
 assert!(edits.keys().all(|i|!deleted.contains(i)));for(i,o)in v.iter().enumerate(){if let Some(w)=edits.get(&i){out.extend_from_slice(w);}else if !deleted.contains(&i){out.push(*o);}}
''' +s[end:]
s=s.replace('EXACT_AND_TARGET_DIAGNOSTIC_NOT_A_SCORE','EXACT_NONCONTIGUOUS_AND_TARGET_DIAGNOSTIC_NOT_A_SCORE')
# Existing fixture/capsule controls still apply; add noncontiguous witnesses.
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn independent_intervening_operations_are_retained(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,5));let ss=discover(&v);assert_eq!(ss.len(),1);let s=&ss[0];let mut w=v[..s.start].to_vec();w.extend(emit(s));for(i,o)in v.iter().enumerate().skip(s.start+1){if !s.queries.contains(&i)&&i!=s.mr&&i!=s.mr+1{w.push(*o);}}for bits in 0..64{for m in [0,u64::MAX]{let x=run(&v,bits,m);let y=run(&w,bits,m);assert_eq!(x,y);}}}
 #[test]fn intervening_target_reader_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::CX,3,NO,5));assert!(discover(&v).is_empty());}
 #[test]fn intervening_target_writer_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,4));assert!(discover(&v).is_empty());}
 #[test]fn intervening_control_writer_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,0));assert!(discover(&v).is_empty());}
''' +s[pos:]
(r/'and_target.rs').write_text(s,encoding='utf-8',newline='\n')
