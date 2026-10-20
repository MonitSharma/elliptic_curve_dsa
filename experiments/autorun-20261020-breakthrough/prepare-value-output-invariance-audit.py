from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-failure-fixture-audit-20261020';r=ex/'breakthrough-value-output-invariance-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore','FAILURE-FIXTURES.json','verify-input.py']:shutil.copyfile(old/n,r/n)
for n in ['io.rs','Cargo.lock','FAILURE-FIXTURES.json']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();start=s.index('fn curve_abstract_audit(');end=s.index('struct AuditWords',start);body=s[start:end]
body=body.replace('let mut concrete_wrong=vec![];','let mut concrete_wrong=vec![];let mut first=vec![];let mut differing=vec![0u64;p.nq];')
needle='concrete_wrong.push(serde_json::json!({"pattern":pattern,';assert body.count(needle)==1
body=body.replace(needle,'if pattern==0{first=sim.qubits.clone();}else{for &q in outputs{differing[q]|=first[q]^sim.qubits[q];}}let mut hash=sha3::Sha3_256::default();for &q in outputs{sha3::Digest::update(&mut hash,sim.qubits[q].to_le_bytes());}let hash=format!("{:x}",sha3::Digest::finalize(hash));'+needle+'"output_sha3":hash,')
body=body.replace('"total_output_bits":outputs.len()*64,','"total_output_bits":outputs.len()*64,"sample_output_invariant_bits":outputs.iter().map(|&q|(!differing[q]).count_ones()as u64).sum::<u64>(),')
body=body.replace('value-known-failure-source-audit-20261020-v1','value-output-invariance-diagnostic-20261020-v1').replace('First128 preserved value-failing scalars','DIAGNOSTIC ONLY: sample invariance is NEVER an exact rejection certificate. First128 preserved value-failing scalars')
s=s[:start]+body+s[end:];(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('value_failure_fixture_audit','value_output_invariance_audit'))
freeze=json.loads((old/'SOURCE-FREEZE.json').read_bytes());freeze['source_files']={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','FAILURE-FIXTURES.json']};freeze['scope']='Diagnostic three-pattern output invariance and full-source fingerprints on same128 preserved failures, not mathematical independence or a rejection certificate. No circuit/nonce/gate change.';(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:(r/n).write_bytes((old/n).read_text().replace(old.name,r.name).replace('value_failure_fixture_audit','value_output_invariance_audit').encode())
(r/'PLAN.md').write_text('''# Diagnostic output invariance before choosing a proof backend

Same first128 existing value-failure scalars, frozen old6192 source,21inherited
native controls and30protected finalvalue comparisons. Record finaloutput SHA3
and bit equality across original three RNG patterns. Sample invariance is NEVER
a proof, nonce rejection criterion or correctness/failure-rate claim. No extra
gate, circuit or nonce selection. This informs the next exact proof method only.
''')
print(r.name)
