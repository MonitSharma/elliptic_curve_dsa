import hashlib,json,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;source=r.parent/'breakthrough-value-normalized-aig-v2-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(source/'run.exit').read_text().strip()=='0';assert '29 passed; 0 failed;'in(source/'tests.log').read_text();f=json.loads((source/'SOURCE-FREEZE.json').read_text());assert all(sha(source/'local-tool'/n)==h for n,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items())
report=json.loads((source/'full-audit.json').read_text());audit=report['curve_audit'];assert audit['cnf_variables']==0 and audit['constant_wrong_bits']==audit['cnf_clauses']==234 and audit['protected_fullstream_comparisons']==3 and report['abstract_audit']['protected_fullstream_comparisons']==24
lines=(source/'wrongpoint.cnf').read_text().splitlines();assert lines[0]=='p cnf 0 234'and len(lines)==235 and all(line.strip()=='0'for line in lines[1:])
# A zero-variable CNF containing an empty clause is unsatisfiable by definition.
# The positive/negative parser controls make the independent check non-vacuous.
def no_assignment_possible(text):
 rows=[x.strip()for x in text.splitlines()if x.strip()and not x.startswith('c')];header=rows.pop(0).split();assert header[:2]==['p','cnf'];n,m=map(int,header[2:]);assert n==0 and len(rows)==m
 for row in rows:assert row=='0'
 return bool(rows)
assert no_assignment_possible('p cnf 0 1\n0\n');assert not no_assignment_possible('p cnf 0 0\n');assert no_assignment_possible((source/'wrongpoint.cnf').read_text())
proof=r/'empty-clause.drat';proof.write_bytes(b'0\n');checker=r.parent/'breakthrough-sat-proof-tools-v5-20261020/tool-repos/drat-trim/drat-trim';assert sha(checker)=='7c3a20e9d34bc78def63b4a05d9839dec3697d1e150e28def354adeec9ab716a'
start=time.monotonic()
with(r/'checker.log').open('xb')as log:p=subprocess.run(['timeout','30',str(checker),str(source/'wrongpoint.cnf'),str(proof)],stdout=log,stderr=subprocess.STDOUT)
(r/'checker.exit').write_text(str(p.returncode)+'\n');checked=p.returncode==0 and's VERIFIED'in(r/'checker.log').read_text()
result={'status':'SOURCE_BOUND_FIXED_INPUT_WRONGPOINT_CERTIFICATE','at_utc':datetime.now(timezone.utc).isoformat(),'fixture':audit['fixture'],'source_stream_sha256':f['expected_stream_sha256'],'source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'audit_result_sha256':sha(source/'full-audit.json'),'native_controls':29,'full_protected_value_comparisons':27,'exact_boolean_nodes':audit['Boolean_nodes'],'build_seconds':audit['build_seconds'],'reachable_output_cnf_variables':0,'constant_wrong_output_bits':234,'independent_zero_variable_cnf_check':'PASS; contains234 empty clauses; empty SAT-formula negativecontrol passes','drat_checker_verified':checked,'drat_checker_exit':p.returncode,'drat_checker_seconds':time.monotonic()-start,'cnf_sha256':sha(source/'wrongpoint.cnf'),'proof_sha256':sha(proof),'checker_sha256':sha(checker),'numeric_ir_cache_sha256':sha(source/'normalized-value-ir.bin.zst'),'nonce_screens':0,'nonce_rejections':0,'scope':'One previously frozen old6192 source and first preserved input only. Exact Boolean source interpretation makes all output literals constants despite arbitrary original measurement outcomes. Independent syntactic zero-variable CNF check certifies contradiction; external checker outcome separately disclosed. This is a fixed-input verifier result, not a general walk filter, a new gate verdict or a quantum resource record. No production nonce skipped.'}
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
