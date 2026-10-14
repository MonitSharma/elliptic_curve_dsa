"""Create an isolated original-source trace variant; no gate changes."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[3]
out=root/'research-output/overnight-20261014/toffoli/carry-trace-v1-source'
out.mkdir(parents=True,exist_ok=True)
source=(root/'agents/product/src/point_add/y15_onefold.rs').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(source).hexdigest()=='879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'
text=source.decode();old='    LOAN_ACTIVE.with(|x|x.set(loan));\n'
assert text.count(old)==1
new=old+'    if loan && std::env::var("TOFFOLI_CARRY_TRACE").is_ok_and(|v|v=="1") { eprintln!("TOFFOLI_CARRY_LIVE payload={:?} fin={fin} ttm={ttm} e_available={} c2_available={} drop={drop}",PAYLOAD_AT.with(|x|x.get()),fin<4,fin==0); }\n'
text=text.replace(old,new)
text+='\n#[cfg(test)]\n#[path="toffoli_carry_recipe_trace_v1.rs"]\nmod toffoli_carry_recipe_trace_v1;\n'
(out/'y15_onefold.rs').write_bytes(text.encode())
fixture=Path(__file__).with_name('toffoli_carry_recipe_trace_v1.rs').read_bytes().replace(b'\r\n',b'\n')
(out/'toffoli_carry_recipe_trace_v1.rs').write_bytes(fixture)
receipt={'status':'trace_source_prepared_no_candidate_gate_change','baseline_source_lf_sha256':hashlib.sha256(source).hexdigest(),
         'source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
         'scope':'Original body resource-only contexts. Extra eprintln gated by research environment; cfg-test fixture. No scored result, no native value/phase claim.'}
Path(__file__).with_name('carry-trace-v1-preparation.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps(receipt))
