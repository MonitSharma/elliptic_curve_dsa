"""Preserve compact inherited failures without reporting diagnostic counts as scores."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[3]
raw=root/'research-output/overnight-20261014/product'
log=raw/'structured-detail.log';text=log.read_text()
cases=[]
for line in text.splitlines():
    if not line.startswith('COUNTEREXAMPLE '):continue
    item={k:v for k,v in (f.split('=',1) for f in line.split()[1:])}
    item['index']=int(item['index']);cases.append(item)
sources={line.split()[1]:line.split()[0] for line in (raw/'structured-detail-source.sha256').read_text().splitlines()}
receipt=dict(baseline_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',baseline_stream_sha256='49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4',comparison_stream_identical=True,protected_evaluator_sha256='b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b',source_sha256=sources,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),packet_sha256=hashlib.sha256((raw/'structured.tsv').read_bytes()).hexdigest(),run_exit_status=0,evidence_kind='structured_research_diagnostic',qualified_score=None,shots=256,unequal_state_batches=0,minus2A=dict(shots=128,classical_failures=128),zero_slope=dict(shots=128,classical_failures=63),phase_garbage_batches=4,ancilla_garbage_batches=0,domain='On-curve distinct-x non-infinity inputs; checked in external source-bound diagnostic.',counterexamples=cases)
out=Path(__file__).with_name('structured-receipt.json');out.write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
print(out)
