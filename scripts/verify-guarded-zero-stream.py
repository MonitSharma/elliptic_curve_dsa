"""Require the generated circuit to differ ONLY by the two proved CCX deletions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

spec=importlib.util.spec_from_file_location('wire',Path(__file__).with_name('analyze-wire-lifetimes.py'))
wire=importlib.util.module_from_spec(spec);spec.loader.exec_module(wire)
base,candidate,proof_path,output=map(Path,sys.argv[1:])
proof=json.loads(proof_path.read_text())
assert hashlib.sha256(base.read_bytes()).hexdigest()==proof['stream_sha256']
expected={h['op']:h['original'] for h in proof['hits']}
assert set(expected)=={5378815,11653340}
new=iter(wire.records(candidate)); removed=[]; kept=0
for i,row in wire.records(base):
    if i in expected:
        assert list(row)==expected[i] and row[0]==13
        removed.append(i)
    else:
        j,actual=next(new)
        assert j==kept and actual==row,(i,j,row,actual)
        kept+=1
assert next(new,None) is None
result=dict(status='exact_whole_stream_deletion_equivalence_verified',
            baseline_sha256=proof['stream_sha256'],candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
            removed_ccx=removed,baseline_operations=i+1,candidate_operations=kept,
            measurements_phase_conditions_registers_and_identity_tail_unchanged=True,
            qualified_score=None)
output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
