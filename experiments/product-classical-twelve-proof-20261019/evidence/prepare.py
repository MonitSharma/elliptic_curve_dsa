"""Read-only instrumentation of the frozen production wider-factor module."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-twelve-native-20261019'
assert (n/'run.exit').read_text().strip()=='0'
native=json.loads((n/'NATIVE-RECEIPT.json').read_text());assert native['raw_sha3_256']=='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
freeze=json.loads((n/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
t=n/'candidate';assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
p=r/'proof';p.mkdir(exist_ok=False)
for name in ['affine_simplify.rs','quadratic_simplify.rs']:shutil.copy2(t/'src/point_add'/name,p/name)
shutil.copytree(t/'src/point_add/classical_wide',p/'wide')
(p/'mod.rs').write_text('mod affine_simplify;\nmod quadratic_simplify;\n#[path="wide/mod.rs"] mod classical_factors_xor;\npub fn run(v:Vec<crate::circuit::Op>)->Vec<crate::circuit::Op>{classical_factors_xor::simplify_classical(v)}\n')
f=p/'wide/mod.rs';s=f.read_text();original=sha(f)
needle=' let mut out=Vec::with_capacity(ops.len());let mut hits=0;';assert s.count(needle)==1;s=s.replace(needle,' let mut audits=vec![];\n'+needle)
needle=' for o in ops{\n';assert s.count(needle)==1;s=s.replace(needle,' for (source_index,o) in ops.into_iter().enumerate(){\n')
needle='  let changed=match o.kind';assert s.count(needle)==1
audit='''  if let Some((bit,other,negated))=witness {
   let encode=|v:&Truth|serde_json::json!({"atoms":v.atoms,"table_hex":v.table.0.iter().rev().map(|x|format!("{:016x}",x)).collect::<String>()});
   audits.push(serde_json::json!({"source_index":source_index,"fields":[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0],
    "base":encode(&state.base_condition),"direct":encode(&if o.c_condition==NO_BIT{Truth::constant(true)}else{state.bits[o.c_condition.0 as usize].clone()}),
    "qa":encode(&state.qubits[o.q_control1.0 as usize]),"qb":encode(&state.qubits[o.q_control2.0 as usize]),
    "other":encode(&state.qubits[other.0 as usize]),"classical":encode(&state.bits[bit]),"bit":bit,"other_wire":other.0,"negated":negated}));
  }
''';s=s.replace(needle,audit+needle)
needle=' eprintln!("CLASSICAL_XOR_FACTORS';assert s.count(needle)==1
s=s.replace(needle,' std::fs::write(std::env::var("AUDIT_OUT").expect("research audit path"),serde_json::to_string_pretty(&audits).unwrap()).unwrap();\n'+needle);f.write_text(s)
for name in ['io.rs','refresh_factors.rs']:shutil.copy2(ws/'product-classical-factors-refresh-20261019'/name,r/name)
(r/'INSTRUMENTATION.json').write_text(json.dumps({'original_frozen_module_sha256':original,'instrumented_sha256':sha(f),'additional_abstraction_queries':0,'scope':'Read-only pre-op truth-table serialization at each selected factor; complete output must remain byte-identical.'},indent=2)+'\n')
