from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-failure-fixture-audit-20261020';r=ex/'breakthrough-value-aig-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore','FAILURE-FIXTURES.json','verify-input.py']:shutil.copyfile(old/n,r/n)
for n in ['io.rs','Cargo.lock','FAILURE-FIXTURES.json']:shutil.copyfile(old/'local-tool'/n,t/n)
shutil.copyfile(a/'value-aig-audit.rs',r/'aig.rs');shutil.copyfile(r/'aig.rs',t/'aig.rs')
s=(old/'audit.rs').read_text();s='mod aig;\n'+s;s=s.replace('let rounds:Vec<(usize,usize,usize)>=vec![];','let l=live(&mut p,&outputs);let c=cancel(&mut p);let rounds=vec![(l,c,p.nodes.len())];').replace('let curve_result=curve_abstract_audit(&p,&ops,&outputs);','let curve_result=aig::audit(&p,&ops,&outputs);');(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('value_failure_fixture_audit','value_aig_audit'))
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f['source_files']={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','aig.rs','FAILURE-FIXTURES.json']};f.update(native_controls=23,scope='Exact scalar Boolean DAG and CNF on FIRST preserved failure input, fixed original6192 source, no nonce/gate/circuit modification. Three full protected value comparisons before export; solver UNSAT proof needed, sampling invariance never used as proof.4mBoolean-node bound aborts inconclusively.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:(r/n).write_bytes((old/n).read_text().replace(old.name,r.name).replace('value_failure_fixture_audit','value_aig_audit').replace('21 passed; 0 failed;','23 passed; 0 failed;').encode())
(r/'PLAN.md').write_text('''# Source-bound scalar Boolean wrongpoint proof experiment

FIRST preserved failure scalar pair only, no input selection by solver outcome.
Same frozen source6192/protected dependencies. Exact captured-SSA values after
one liveness/cancel round. Scalar Boolean AND/XOR/ITE DAG with structural
identities only, all random bits arbitrary, original RNG slot mapping retained.
4million node budget aborts inconclusively. Native21 controls plus2DAG truth/
cancellation controls, three fullprotected finalvalue comparisons before CNF.
Export reachable DAG as exact Tseitin CNF and require ALL output bits equal
reference P+A. SAT means inconclusive; UNSAT certifies wrong point for this one
input, not a general model and not a production rejection filter. Separate
solver encoding qualification/source/hash checks and timeout required. No
nonce screened or rejected; prior statistical gate verdict unchanged.
''');print(r.name)
