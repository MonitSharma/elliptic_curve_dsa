"""Verify the immutable snapshot and write concise autonomous handoff notes."""
from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent;root=r.parents[1]
receipt=json.loads((r/'CHECKPOINT-EVIDENCE.json').read_text());archive=r/receipt['archive']
assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()==receipt['sha256']
with tarfile.open(archive) as a:
    m=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
    for name,item in m['included_files'].items():
        raw=a.extractfile(name).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
    dest=r/'evidence';dest.mkdir(exist_ok=False)
    for member in a.getmembers():
        assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        p=dest/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(a.extractfile(member).read())
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ALL_IMMUTABLE_CHECKPOINT_HASHES_VERIFIED','archive':receipt,'files':len(m['included_files'])},indent=2)+'\n')
block='''## 19 October, 16:14: parent4 frozen search active; complete proof qualified

All27 public-parent product identities plus the zero row now have universal
source-bound SAT proofs and a passing full integration audit. The disabled
filter passed its complete own-seed/full-state/physical-RNG/partial-batch
qualification. The reviewed operational port passed source and prefix checks.
The same parent4 source and single passing statistical gate remain frozen.

Ascending search started16:05 Singapore, PID602346, four14-thread workers;
48-hour cap. Queue-only terminal audit/native benchmark watcher PID610395
will verify every lower nonce and unchanged benchmark on a pass. No scored
result yet. Fresh public product is still939192464 (Q1234/T761096).
An independent exact64-term Boolean-polynomial source screen is running on
one core (PID624226); it does not modify the frozen candidate or search.

[Active search](../experiments/parent4-operational-sat-20261019/STATUS.md) ·
[Complete proof](../experiments/product-parent-sat-20261019/CHECKPOINT-1609.md) ·
[Automatic final verification](../experiments/parent4-final-sat-20261019/STATUS.md).

'''
for name in ('docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'):
    p=root/name;s=p.read_text(encoding='utf-8');head,body=s.split('\n',1);p.write_text(head+'\n\n'+block+body.lstrip('\n'),encoding='utf-8')
for name in ('experiments/product-parent-sat-20261019/STATUS.md','experiments/product-pareto-20261019/PARENT4-SUBMISSION-STATUS.md'):
    p=root/name;s=p.read_text(encoding='utf-8');head,body=s.split('\n',1)
    p.write_text(head+'\n\n## 19 October,16:14: complete proof and filter passed; ascending search active\n\n'
        'See [current checkpoint](../product-parent-sat-20261019/CHECKPOINT-1609.md). '
        'Search PID602346 and automatic final-verification watcher PID610395 are active. '
        'Historical checkpoints below retain their original timing and outcomes; '
        'the84-stage candidate subsequently failed its single gate and is ineligible. '
        'No new benchmark result yet.\n\n'+body.lstrip('\n'),encoding='utf-8')
p=r/'STATUS.md';s=p.read_text();s=s.replace('19 October 2026, autonomous continuation. No new scored result yet.',
    '19 October2026,16:14 Singapore. Search active since16:05, PID602346, four14-thread workers. '
    'Complete source/order/prefix controls passed; acceptance SHA2564e3b1ce9a4f36ec1a781a5e304776a79831d6b70ff82fc248f7bb5e0c92b7ec9. '
    'Automatic audit/native benchmark watcher PID610395 waits for termination. No scored result yet.')
s=s.replace('the search has not yet started.','the search is now active.').replace('Remaining: finish operational controls; launch the frozen ascending search;','Remaining: finish the frozen ascending search;')
p.write_text(s)
print('Verified',len(m['included_files']),'checkpoint files; updated handoff')
