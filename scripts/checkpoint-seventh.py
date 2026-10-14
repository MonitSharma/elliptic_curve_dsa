"""Select only explicit frozen completed sets and coordinator evidence."""
import datetime
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1];CYCLE=ROOT/'experiments/overnight-20261014'
groups=['product/checkpoint-seventh-manifest.json','qubits/seventh-fixed2379-manifest.json',
        'toffoli/consumer-carry-v18-checkpoint-receipt.json','toffoli/sequential-v19-checkpoint-receipt.json',
        'toffoli/cubic-producer-v23-checkpoint-receipt.json','toffoli/consume-seven-v25-checkpoint-receipt.json']
selected=set()
for name in groups:
    p=CYCLE/name;selected.add(p.relative_to(ROOT).as_posix());d=json.loads(p.read_text(encoding='utf-8-sig'))
    entries=d['files']
    if isinstance(entries,list):selected.update(e['path']for e in entries)
    else:selected.update((p.parent/n).relative_to(ROOT).as_posix()for n in entries)
selected.update('experiments/overnight-20261014/coordinator/'+n for n in[
 'ht25-ideal-packet.json','ht25-precision-results.md','mixedhr23-structured-model.json','mixedhr-capacity-results.md',
 'public-product-leader-source-review.md','constant-measurements-v1-analysis.json','constant-measurements-v1-receipt.json',
 'headflag-terminal-collector-receipt.json'])
selected.update('scripts/'+n for n in['analyze-constant-measurements.py','server-constant-measurements.sh',
 'test_constant_measurements.py','audit-ht25-ideal-packet.py','construct-mixedhr-capacity.py',
 'server-headflag-terminal-collector.sh','bind-checkpoint-manifests.py','checkpoint-seventh.py'])
selected.update(['docs/SERVER_HANDOFF.md','docs/experiment-outcomes.md','docs/overnight-20261014.md','experiments/overnight-20261014/cycle.json'])
cycle=CYCLE/'cycle.json';d=json.loads(cycle.read_text())
d['seventh_checkpoint']={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'original_submission_ready':False,'original_qualified_candidates':[],
 'headflag_official_benchmark':{'native_pid':2662310,'status':'PENDING_NO_AGGREGATE_RESULT','collector_pid':2740181,'collector':'Bounded24hnohupwait; exactsource/stream/score checks once terminal; never reruns benchmark'},
 'qubit_completed_diagnosis':'Fixed2379 arithmetic failure inherited at clean c95 primitive. MixedHR22 lacks structural proof; structuredmodel fixtures motivate restoring23. HT25model stillneedshead32 precision; quantum repair remainscomponent-only.',
 'product_completed_proofs':'Rail109 andfold75/104 deterministic value faults over allfutureinternalMR on finiteoriginalprefix contexts; pastMRfixed/incomingphaseadditive.',
 'constructor_lower_bound':'Atleast27ANDs for specified all14-input straightlineXOR/AND value contract, conditionaltrustedZ3UNSAT and independentlyauditedencoding; no fullpoint resourceclaim.',
 'negative_routes':'v17/v18/v20–23 selectedconstructor/scalar/producer-domain interfaces close withoutcompletewitness; constantmeasurement scan no directguardedToffoli opportunity.',
 'active_repairs_excluded':'HT25 storage/precision andrepair57 actualfold prototype/component variants, laterconsumer queries. Their own receipts will be frozen separately.'}
cycle.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
for name in selected:
    p=ROOT/name;assert p.is_file(),name
    assert not name.startswith('agents/'),name
    if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
    if p.suffix=='.patch':
        diffs=re.findall(r'^diff --git a/(.*?) b/(.*?)$',p.read_text(encoding='utf8'),re.M)
        assert diffs and all(a.startswith('src/point_add/')and b.startswith('src/point_add/')for a,b in diffs),name
    assert p.stat().st_size<=2_000_000,('Oversized compact artifact',name)
out=ROOT/'research-output/overnight-20261014/seventh-stage-paths.json'
out.write_text(json.dumps(sorted(selected),indent=2)+'\n',encoding='utf8')
print(json.dumps({'selected_files':len(selected),'bytes':sum((ROOT/n).stat().st_size for n in selected)}))
