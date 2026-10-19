"""Instrument a research COPY without changing the frozen candidate pass."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;f=ws/'product-classical-factors-refresh-20261019'
p=r/'proof';p.mkdir(exist_ok=False)
for name in ['mod.rs','affine_simplify.rs','quadratic_simplify.rs','classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']:
    shutil.copy2(f/'proof'/name,p/name)
for name in ['io.rs','refresh_factors.rs']:
    shutil.copy2(f/name,r/name)
s=(p/'classical_factors_xor.rs').read_text()
needle=' let mut out=Vec::with_capacity(ops.len());let mut hits=0;'
assert s.count(needle)==1;s=s.replace(needle,' let mut audits=vec![];\n'+needle)
needle=' for o in ops{\n';assert s.count(needle)==1;s=s.replace(needle,' for (source_index,o) in ops.into_iter().enumerate(){\n')
needle='  let changed=match o.kind';assert s.count(needle)==1
audit='''  if let Some((bit,other,negated))=witness {
   let encode=|v:&Truth|serde_json::json!({"atoms":v.atoms,"table_hex":format!("{:032x}",v.table)});
   audits.push(serde_json::json!({"source_index":source_index,"fields":[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0],
    "base":encode(&state.base_condition),"direct":encode(&if o.c_condition==NO_BIT{Truth::constant(true)}else{state.bits[o.c_condition.0 as usize].clone()}),
    "qa":encode(&state.qubits[o.q_control1.0 as usize]),"qb":encode(&state.qubits[o.q_control2.0 as usize]),
    "other":encode(&state.qubits[other.0 as usize]),"classical":encode(&state.bits[bit]),"bit":bit,"other_wire":other.0,"negated":negated}));
  }
'''
s=s.replace(needle,audit+needle)
needle=' eprintln!("CLASSICAL_XOR_FACTORS';assert s.count(needle)==1
s=s.replace(needle,' std::fs::write(std::env::var("AUDIT_OUT").expect("research audit path"),serde_json::to_string_pretty(&audits).unwrap()).unwrap();\n'+needle)
(p/'classical_factors_xor.rs').write_text(s)
original=f/'proof/classical_factors_xor.rs'
(r/'INSTRUMENTATION.json').write_text(json.dumps({'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'instrumented_sha256':hashlib.sha256((p/'classical_factors_xor.rs').read_bytes()).hexdigest(),'additional_state_operations':0,'added_code':'Read-only serialization of pre-op Truth values at witnesses; enumerate index and terminal JSON write. No extra abstraction queries or fresh atoms.'},indent=2)+'\n')
