import hashlib,json,shutil
from pathlib import Path
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-failure-fixture-audit-20261020';r=ex/'breakthrough-value-affine-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore','FAILURE-FIXTURES.json','verify-input.py']:shutil.copyfile(old/n,r/n)
for n in ['io.rs','Cargo.lock','FAILURE-FIXTURES.json']:shutil.copyfile(old/'local-tool'/n,t/n)
shutil.copyfile(a/'value-affine-audit.rs',r/'affine.rs');shutil.copyfile(r/'affine.rs',t/'affine.rs')
s=(old/'audit.rs').read_text();s='mod affine;\n'+s;needle='let rounds:Vec<(usize,usize,usize)>=vec![];';assert s.count(needle)==1;s=s.replace(needle,'let l=live(&mut p,&outputs);let c=cancel(&mut p);let rounds=vec![(l,c,p.nodes.len())];')
start=s.index('fn curve_abstract_audit(');end=s.index('struct AuditWords',start);body=s[start:end].replace('let abstract_q=abstract_eval(p,&q,&bits);','let abstract_q=affine::eval(p,&q,&bits);').replace('value-known-failure-source-audit-20261020-v1','value-bounded-anf-failure-audit-20261020-v1').replace('Raw captured-SSA IR without static optimization','Captured-SSA IR after one exact liveness/cancellation round, bounded Boolean polynomial overapproximation');s=s[:start]+body+s[end:];(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
manifest=(old/'local-tool/Cargo.toml').read_text().replace('value_failure_fixture_audit','value_affine_audit');(t/'Cargo.toml').write_text(manifest)
freeze=json.loads((old/'SOURCE-FREEZE.json').read_bytes());freeze['source_files']={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','affine.rs','FAILURE-FIXTURES.json']};freeze.update(native_controls=23,scope='Verification-only bounded Boolean polynomial certificates on unchanged old stream, first128 preserved failures. Polynomial identities exact, opaque atoms overapproximate; no certainty from sampling. At most8terms/degree4, exact structural memoization capped65536; >2million monomials returns ALLUNKNOWN. No nonce screened/rejected or gate/circuit modified.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name).replace('value_failure_fixture_audit','value_affine_audit').replace('21 passed; 0 failed;','23 passed; 0 failed;');(r/n).write_bytes(s.encode())
(r/'PLAN.md').write_text('''# Bounded Boolean polynomial rejection-certificate research

Same immutable oldproduct6192,17protected files and first128 oldvalue-failure
scalar pairs. One exact value liveness/cancellation round; no fixedpoint wait.
Symbolically propagate XOR/AND/ITE over Boolean monomials with64lane coefficient
masks. Keep at most8terms anddegree4; larger expressions become opaque atoms
representing arbitrary unknown words. Exact structural memoization, no hash-only
identities. Larger cache misses get distinct opaque atoms, losing precision only.
If2million monomials exceeded return ALLUNKNOWN. A bit is certified only when
all nonconstant coefficients on that bit cancel. Random values never fixed.
Concrete truth fields are test oracles only and NEVER influence certificates.

Retain21 native/protected controls; add complete64assignments of6variables over
1000 symbolic expressions and correlation/opaque-bound regressions (23total).
Then6protected fullsource comparisons on128known-failing scalar pairs, plus24
arbitrary-fixture comparisons. No nonce rejected, no statistical verdict rerun,
no quantum resource count or submission. Full independent originalFS/source/
curve qualification still needed for any future actual rejection filter.
''')
print(r.name)
