import json
from pathlib import Path
root = Path(__file__).parent / "evidence"
def rows(name):
    return {r["nonce"]: r for r in map(json.loads, (root/name).read_text().splitlines())}
a=rows("fast-screen-1-128.jsonl")
b=rows("reference-screen-1-128.jsonl")
assert a.keys()==b.keys()
for n in a:
    for k in ("pass","batches_run","kind"):
        assert a[n][k]==b[n][k], (n,k,a[n],b[n])
report=dict(nonces=len(a),exact_agreement=len(a),nonce_first=min(a),nonce_last=max(a),
            fast_thread_seconds=sum(r["secs"] for r in a.values()),
            reference_thread_seconds=sum(r["secs"] for r in b.values()),
            batches=sum(r["batches_run"] for r in a.values()),
            scope="Exact values, phase and ancilla decisions; original packet RNG and batch order preserved.")
report["speedup"]=report["reference_thread_seconds"]/report["fast_thread_seconds"]
(root/"nonce-differential.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
