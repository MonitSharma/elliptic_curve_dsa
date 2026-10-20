"""Fix only test-export formatting; Cargo and runtime source stay untouched."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
failed=r/'failed-undeclared-json-export-v1';failed.mkdir(exist_ok=False)
for name in['tests.log','run.exit','SOURCE_FREEZE.json','source.patch','core_rank_tests.rs']:shutil.copyfile(r/name,failed/name)
p=t/'src/point_add/y15_onefold.rs';before=p.read_bytes();start=before.index(b'        let data=serde_json::json!(');end=before.index(b'\n    }\n}',start)
replacement=b'''        let forms=output.iter().map(|a|format!("{{\\\"wires\\\":{:?},\\\"one\\\":{}}}",a.w.iter().map(|q|q.0).collect::<Vec<_>>(),a.one)).collect::<Vec<_>>().join(",");
        let data=format!("{{\\\"source_qubits\\\":{:?},\\\"qubit_truth_words\\\":{:?},\\\"output_forms\\\":[{}],\\\"emitted_ccx\\\":{},\\\"held_records\\\":{},\\\"supported_signed_inputs_verified\\\":{},\\\"outside_promised_range_math_mismatches\\\":{:?},\\\"scope\\\":\\\"Actual unmodified eight-input function; only signed[-70,7] promised. No runtime circuit change.\\\"}}",source.iter().map(|q|q.0).collect::<Vec<_>>(),truth,forms,ops.iter().filter(|o|o.kind==OperationType::CCX).count(),records.len(),supported,outside_mismatches);
        std::fs::write("../CORE-TRUTH.json",data).unwrap();'''
after=before[:start]+replacement+before[end:];marker=b'\n#[cfg(test)]mod core_rank_audit_tests'
assert before.split(marker)[0]==after.split(marker)[0];p.write_bytes(after)
(r/'core_rank_tests-v2.rs').write_bytes(marker+after.split(marker)[1])
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['repair']='Test-only JSON formatting without an undeclared serde_json dependency. Runtime prefix unchanged; Cargo/protected17 unchanged.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
