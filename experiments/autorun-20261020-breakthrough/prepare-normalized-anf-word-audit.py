from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-word-value-audit-20261020';r=ex/'breakthrough-normalized-anf-word-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(old/'run.exit').read_text().strip()=='0'
for n in ['Cargo.lock','io.rs','aig.rs','FAILURE-FIXTURES.json','ir_cache.rs','word.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
anf=(a/'value-affine-audit-v3.rs').read_text();(t/'affine.rs').write_text(anf);(r/'affine.rs').write_text(anf)
s=(old/'audit.rs').read_text().replace('mod ir_cache;mod word;','mod ir_cache;mod word;mod affine;mod anf_audit;').replace('let audit=word::audit(&p,&ops,&outputs,&fixtures);','let audit=anf_audit::audit(&p,&ops,&outputs,&fixtures);');(t/'audit.rs').write_text(s);(r/'audit.rs').write_text(s)
word=(old/'word.rs').read_text();s=word[word.index('pub(super)fn audit('):word.index('#[cfg(test)]mod tests')]
s=s.replace('p:&Program','p:&super::Program')
needle='let(a,result)=match construct(p,&q,&bits){Ok(v)=>v,Err(at)=>{rows.push(serde_json::json!({"batch":batch,"status":"INCONCLUSIVE_NODE_BUDGET","at":at}));continue;}};';assert s.count(needle)==1;s=s.replace(needle,'let result=super::affine::eval(p,&q,&bits);')
s=s.replace('let(z,o)=a.known(result[q]);','let(z,o)=(result[q].z,result[q].o);').replace('let values=a.evaluate(&words);','let mut exact=q.clone();super::eval(p,&mut exact,&bits,&words);')
s=s.replace('assert_eq!(a.value(result[q],&values)&valid,sim.qubits[q]&valid,"wordAIG/protected batch{batch} pattern{pattern} wire{q}");','assert_eq!(exact[q]&valid,sim.qubits[q]&valid,"numericIR/protected batch{batch} pattern{pattern} wire{q}");let tv=result[q];assert_eq!(sim.qubits[q]&(tv.z|tv.o)&valid,tv.o&valid,"ANF knownbit/protected mismatch");')
s=s.replace('"word_boolean_nodes":a.nodes.len(),','').replace('nodes={} seconds={seconds}','seconds={seconds}').replace(',a.nodes.len());',');')
s=s.replace('EXACT_SOURCE_WORD_BOOLEAN_VERIFIER_FIXTURE_AUDIT_NOT_A_NONCE_SCREEN','EXACT_SOURCE_NORMALIZED_ANF_VERIFIER_FIXTURE_AUDIT_NOT_A_NONCE_SCREEN')
(t/'anf_audit.rs').write_text(s);(r/'anf_audit.rs').write_text(s)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('word_value_audit','anf_word_value_audit'))
for n in ['WORD-FIXTURES.json','.gitignore','.gitattributes','verify.py']:shutil.copyfile(old/n,r/n)
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','aig.rs','audit.rs','ir_cache.rs','word.rs','affine.rs','anf_audit.rs','FAILURE-FIXTURES.json']},native_controls=37,scope='Reuse exact previously qualified boundedANFv3 (word-mask coefficients, <=8terms/degree4, fullkey opaque aliases,16mmonomial budget/soundTVfallback) on NEW fully semantic/cofactor-normalized IR with310remainingCRNG instead of old5690. Same frozen6192 source/cache/192fixtures. Prior29+cache2+word3+ANF3=37native;24cache protected comparisons, then9full protected numericIR/ANFknownbit checks. Truthoracles nevercertificates, unknownneverrejects. No gate/nonce/quantumsource or score change. OriginalwordDAG1m budget failures retained; this changes algebra rather than blindly increasingbudget.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('word_value_audit','anf_word_value_audit').replace('34 passed; 0 failed;','37 passed; 0 failed;');(r/'run-local.sh').write_bytes(s.encode());(r/'PLAN.md').write_text('# Masked bounded ANF on the fully normalized IR\n\n'+f['scope']+'\n')
(old/'STATUS.md').write_text('# INCONCLUSIVE: all three word-DAG groups hit node budget\n\nNative34 and24fullprotected cache comparisons PASS. All3fixed64input groups stop at1mBoolean nodes aroundsource node2.43m before word/fullprotected group comparisons; no knownbit or wrongpoint certificate. No nonce rejected. Preserve exact source/logs/results; next front uses already qualified maskedANF on the stronger normalizedIR rather than raising this budget.\n');print(r.name)
