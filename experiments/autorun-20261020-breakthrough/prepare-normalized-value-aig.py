from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-value-normalized-aig-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
old=ex/'breakthrough-value-semantic-guards-audit-v2-20261020'
for n in ['Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
source=(ex/'breakthrough-value-cofactor-qualification-20261020/local-tool/audit.rs').read_text()
assert source.startswith((old/'audit.rs').read_text())
source='mod aig;\n'+source
needle='let curve_result=curve_abstract_audit(&p,&ops,&outputs);';assert source.count(needle)==1
source=source.replace(needle,'let curve_result=aig::audit(&p,&ops,&outputs);')
# Save a compact numeric IR for later independent backend experiments. The
# evaluator never reloads this in the present experiment.
needle='let abstract_result=full_abstract_audit(&p,&ops,&outputs);';assert source.count(needle)==1
source=source.replace(needle,'''let mut raw=Vec::new();raw.extend_from_slice(b"VALUEIR1");for v in[p.nq,p.nb,p.versions,p.rng,p.inputs.len(),p.guards.len(),p.nodes.len(),outputs.len()]{raw.extend_from_slice(&(v as u64).to_le_bytes());}for &v in p.inputs.iter().chain(outputs){raw.extend_from_slice(&(v as u32).to_le_bytes());}for g in &p.guards{raw.extend_from_slice(&(g.len()as u32).to_le_bytes());for &v in g{raw.extend_from_slice(&v.to_le_bytes());}}for n in &p.nodes{raw.push(n.k);for v in[n.a,n.b,n.t,n.g,n.r,n.source]{raw.extend_from_slice(&v.to_le_bytes());}}std::fs::write("normalized-value-ir.bin.zst",zstd::encode_all(&raw[..],3).unwrap()).unwrap();drop(raw);'''+needle)
(t/'audit.rs').write_text(source);(r/'audit.rs').write_text(source)
aig=(ex/'breakthrough-value-aig-cnf-qualification-20261020/local-tool/aig.rs').read_text()
# The original qualified AIG/CNF producer remains byte-identical.
(t/'aig.rs').write_text(aig);(r/'aig.rs').write_text(aig)
for dest in [t/'FAILURE-FIXTURES.json',r/'FAILURE-FIXTURES.json']:
 shutil.copyfile(ex/'breakthrough-value-aig-audit-20261020/FAILURE-FIXTURES.json',dest)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('value_semantic_guards_v2_audit','value_normalized_aig_audit'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha(t/n)for n in['Cargo.toml','Cargo.lock','io.rs','audit.rs','aig.rs','FAILURE-FIXTURES.json']},native_controls=29,scope='Fixed original6192 source and FIRST previously declared failing input, with all measurement outcomes existential. Complete exact semantic/cofactor IR normalization before unchanged qualified AIG/CNF producer. All26 semantic controls plus3 AIG/CNF controls and24+3 full protected value comparisons. Numeric IR export is a cache artifact only, not loaded or used as a certificate. No gate/nonce/circuit change or quantum resource claim.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
shutil.copyfile(old/'verify-input.py',r/'verify-input.py')
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('value_semantic_guards_v2_audit','value_normalized_aig_audit').replace('25 passed; 0 failed;','29 passed; 0 failed;')
(r/'run-local.sh').write_bytes(s.encode());(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.cnf\nnormalized-value-ir.bin.zst\n');(r/'.gitattributes').write_text('* -text\n')
(r/'PLAN.md').write_text('''# Exact Boolean proof after complete semantic guard normalization

The prior one-round AIG had 3.13m variables and its proof checker timed out.
The exact semantic/cofactor IR removes most live measurement dependencies.
Run complete normalization on the same frozen6192 circuit, then apply the
byte-identical qualified AIG/CNF producer to the SAME first preserved failure.
Keep all original RNG outcomes arbitrary. Native29 plus24+3 protected value
comparisons required before treating the export as valid. No solver result
alone is a checked proof. No nonce screened/rejected, no statistical gate
rerun or circuit tuning. Numeric IR cache saved for future backend research;
it is not read or trusted by this experiment. All counts are verifier-only.
''')
print(r.name)
