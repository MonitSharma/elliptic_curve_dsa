"""Select frozen final evidence and explicitly named handoff artifacts."""
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
CYCLE=ROOT/'experiments/overnight-20261014'
a=argparse.ArgumentParser(description=__doc__)
a.add_argument('--extra-manifest',action='append',default=[])
args=a.parse_args()
groups=['product/checkpoint-final-product-manifest-v2.json',
        'qubits/ht25-completed-manifest.json','toffoli/final-track-checkpoint-receipt.json']+args.extra_manifest
selected=set()
for name in groups:
    p=CYCLE/name
    selected.add(p.relative_to(ROOT).as_posix())
    d=json.loads(p.read_text(encoding='utf-8-sig'))
    entries=d['files']
    if isinstance(entries,list):selected.update(e['path'] for e in entries)
    else:selected.update((p.parent/n).relative_to(ROOT).as_posix() for n in entries)
selected.update(['scripts/checkpoint-final.py','scripts/bind-checkpoint-manifests.py',
 'scripts/validate-final-checkpoint.py','README.md','docs/research-plan.md',
 'scripts/server-headflag-fixed-packet.sh',
 'docs/SERVER_HANDOFF.md','docs/experiment-outcomes.md','docs/overnight-20261014.md',
 'docs/overnight-final-report.md','docs/data/latest-leaderboard.json',
 'docs/frontier-results.md','docs/figures/frontier.png',
 'experiments/overnight-20261014/cycle.json',
 'experiments/overnight-20261014/coordinator/final-handoff.json',
 'experiments/overnight-20261014/coordinator/headflag-terminal-collector-receipt.json',
 'experiments/overnight-20261014/coordinator/headflag-v1-full-failed-receipt.json',
 'experiments/overnight-20261014/coordinator/headflag-v1-full-failed.log.gz',
 'experiments/overnight-20261014/coordinator/headflag-fixed-packet-receipt.json',
 'experiments/overnight-20261014/coordinator/headflag-fixed-packet-full-export.log.gz',
 'experiments/overnight-20261014/coordinator/bankswap-v2-final-generation-receipt.json',
 'experiments/overnight-20261014/coordinator/ht25-bankswap-v2-stream-metadata.json',
 'experiments/overnight-20261014/coordinator/ht25-bankswap-v2-parser-admission.json',
 'experiments/overnight-20261014/coordinator/ht25-bankswap-v2-full-build-terminal.log.gz',
 'experiments/overnight-20261014/coordinator/mixedhr-capacity-results.md',
 'experiments/overnight-20261014/qubits/qubit-ht25-v9-full-build.sh'])
selected.add('experiments/overnight-20261014/product/prepare-seventh-checkpoint-manifest.py')
selected.update('experiments/overnight-20261014/'+n for n in[
 'product/checkpoint-final-product-manifest.json',
 'toffoli/bankswap-review-checkpoint-v1.json','toffoli/bankswap-review-checkpoint-v2.json'])
for name in selected:
    p=ROOT/name
    assert p.is_file(),name
    assert not name.startswith('agents/'),name
    if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
    if p.suffix=='.patch':
        content=p.read_text(encoding='utf8')
        diffs=re.findall(r'^diff --git a/(.*?) b/(.*?)$',content,re.M)
        if p.name=='ht25-v9-done-private-fixture.patch':
            # Research-only test instrumentation delta, not a contestant patch.
            assert re.findall(r'^(?:---|\+\+\+) (.*)$',content,re.M)==['prepared15/tests_midg_k24.rs','private16/tests_midg_k24.rs'],name
        else:assert diffs and all(x.startswith('src/point_add/') and y.startswith('src/point_add/') for x,y in diffs),name
    assert p.stat().st_size<=2_000_000,('Oversized compact artifact',name)
out=ROOT/'research-output/overnight-20261014/final-stage-paths.json'
out.write_text(json.dumps(sorted(selected),indent=2)+'\n',encoding='utf8')
print(json.dumps({'selected_files':len(selected),'bytes':sum((ROOT/n).stat().st_size for n in selected),'manifests':groups}))
