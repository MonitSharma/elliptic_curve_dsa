"""Instrument a separate copy; preserve the completed support allocator source."""
from pathlib import Path
r=Path(__file__).resolve().parent
src=(r.parent/'product-support-tight-20261019/tight_color.rs').read_text()
src=src.replace('fn color(v:&[Op])->', '''fn peak_at(peaks:&mut Vec<(usize,usize)>,i:usize){if let Some(p)=peaks.last_mut(){if i<=p.1+1{p.1=i;return;}}peaks.push((i,i));}
fn color(v:&[Op])->''',1)
needle=' for(i,original)in v.iter().enumerate(){let mut o=*original;'
assert src.count(needle)==1
src=src.replace(needle,''' let scan=std::env::var("CARRY_SCAN").ok().map(|p|serde_json::from_str::<serde_json::Value>(&std::fs::read_to_string(p).unwrap()).unwrap());
 let mut entry=std::collections::BTreeMap::new();let mut entry_ok=vec![];
 if let Some(s)=&scan{for (j,x) in s["cells"].as_array().unwrap().iter().enumerate(){entry.insert(x["start"].as_u64().unwrap() as usize,(j,[x["a"].as_u64().unwrap() as usize,x["b"].as_u64().unwrap() as usize,x["c"].as_u64().unwrap() as usize,x["t"].as_u64().unwrap() as usize]));entry_ok.push(false);}}
 let mut full_width_regions=vec![];
 for(i,original)in v.iter().enumerate(){let mut o=*original;
  if nq-free.len()==nq{peak_at(&mut full_width_regions,i);}
  if let Some(&(j,[a,b,c,t]))=entry.get(&i){entry_ok[j]=q[a].is_yes()&&q[b].is_yes()&&q[c].is_yes()&&q[t].is_no();}
''',1)
needle='  live_peak=live_peak.max(nq-free.len());'
assert src.count(needle)==1
src=src.replace(needle,needle+'\n  if nq-free.len()==nq{peak_at(&mut full_width_regions,i);}',1)
needle='  if i%1_000_000==0'
assert src.count(needle)==1
src=src.replace(needle,'  if nq-free.len()==nq{peak_at(&mut full_width_regions,i);}\n'+needle,1)
needle='"status":"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE",'
assert src.count(needle)==1
src=src.replace(needle,needle+'"full_width_regions":full_width_regions,"carry_entry_all_operands_unknown_and_target_zero":entry_ok,',1)
(r/'peak_profile.rs').write_text(src,encoding='utf-8',newline='\n')
cargo=(r/'Cargo.toml').read_text()
if 'name="carry_peak_profile"' not in cargo:
    cargo+='\n[[bin]]\nname="carry_peak_profile"\npath="peak_profile.rs"\n'
(r/'Cargo.toml').write_text(cargo,encoding='utf-8',newline='\n')
