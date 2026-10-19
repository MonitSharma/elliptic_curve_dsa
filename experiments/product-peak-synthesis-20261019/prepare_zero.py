"""Derive a zero-event prover from the previously tested exact value engine."""
from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'recompute.rs').read_text()
s=s.replace('assert!(args.len()==5,"input output-prefix expression-cap minimum-donor"); let minimum:u64=args[4].parse().unwrap();',
            'assert!(args.len()==4,"input output-prefix expression-cap");')
assert 'let minimum:u64' not in s
needle=' let mut exact_reductions_unconditional=0;'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n let mut zero_events:Vec<(usize,u64)>=vec![];')
s=s.replace('  unwrap.observe(i,o,&eff,&q,&c,&mut alg);','  // This pass observes exact zero values only; it does not unwrap gates.')
s=s.replace('   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::DebugPrint=>{},',
            '   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::DebugPrint=>{},')
needle='  if i%1000000==0{'
assert s.count(needle)==1
s=s.replace(needle,'''  if stack.is_empty() && !matches!(o.kind,K::R|K::Hmr) {
   for w in [o.q_target.0,if o.kind==K::Swap{o.q_control1.0}else{no}]{
    if w!=no && q[w as usize].is_empty(){zero_events.push((i,w));}
   }
  }
'''+needle)
lo=s.index(' let mut deletions=HashSet::new();')
hi=s.index('\n#[cfg(test)]mod tests{',lo)
s=s[:lo]+'''
 let result=serde_json::json!({"status":"EXACT_ZERO_EVENT_CERTIFICATE_DIAGNOSTIC","input":args[1],"input_count":ops.len(),"input_sha3_256":hash(&ops),"expression_cap":alg.cap,"truncations":alg.truncations,"zero_events":zero_events,"event_count":zero_events.len()});
 std::fs::write(format!("{out}.json"),serde_json::to_string_pretty(&result).unwrap()).unwrap();
 println!("exact zero events={}",zero_events.len());
}
'''+s[hi:]
(r/'zero.rs').write_text(s)
