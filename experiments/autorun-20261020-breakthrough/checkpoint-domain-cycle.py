"""Save additive research status without staging pre-existing document edits."""
import difflib,gzip,hashlib,json,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc)
latest=json.loads((root/'experiments/breakthrough-assessment-20261020/LATEST.json').read_bytes())
snapshot=root/'experiments/breakthrough-assessment-20261020'/latest['snapshot']
raw=(snapshot/'public-submissions.json').read_bytes();compressed=gzip.compress(raw,mtime=0)
(snapshot/'public-submissions.json.gz').write_bytes(compressed)
(snapshot/'public-submissions.json.gz.manifest.json').write_text(json.dumps({'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),
    'gzip_bytes':len(compressed),'gzip_sha256':hashlib.sha256(compressed).hexdigest()},indent=2)+'\n')
reports={
'breakthrough-subphase-20261020':'''# Legacy raw-subphase attribution completed

Diagnostic only; no scored result. Both native repair-v2 and refinement exit0.
The entire raw stream exactly matches admitted13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b.
All512x64 refined rows agree with the previous partition in every unchanged
field. Protected17 files remain unchanged; initial compile failure preserved.

The legacy pacc names overlap and sometimes name identical spans. Selecting
the smallest span with alphabetical tie breaking does not distinguish fused
payload arithmetic from pure rotations. Do not interpret its barrel/rail
categories as pure operation families. The direct function-membership profile
in breakthrough-domain-profile-20261020 supersedes those semantic labels.
The51-member evidence archive and every included member verify locally.
No final statistical gate, nonce search, source candidate or scored improvement.
''',
'breakthrough-domain-profile-20261020':'''# Direct raw payload and rotation membership

Completed diagnostic on the exact accepted raw arithmetic stream; no new
complete point-add result. Full stream hash13f6ffc3... and protected17 match.
Boolean union of explicit payload wrappers and actual rot4 calls partitions
all11263273 raw operations into722 segments, without legacy name tie breaking.
All512 existing diagnostic rows match the previous unchanged circuit in every
nonregional field; eight full protected scalar controls also pass.

Diagnostic mean executed Toffolis: divide payload182507.06, comprising
130555.06 arithmetic and51952 rotations; multiply payload186735.64, comprising
134401.64 arithmetic and52334 rotations. Other includes rail operations,
unwrapped special tick0, setup and endpoints; it is not a pure rail category.
These are raw pre-post-pass observations, not final optimized scores.

The26-member evidence archive and every member verify locally. Replay runtime
is bound to the previously verified baseline profiler. All supervisors are
terminal. No candidate, final gate or nonce search was run.
''',
'breakthrough-cofactor-rotation-20261020':'''# Exact cofactor rotation transfer and integration budget

Eight unique native component tests pass. The incumbent three-reflection
construction lowers a sixteen-bit signed cofactor update from93 to86 CCX.
All8160 small-word basis cases n3..10, forward/inverse gate formulas n9..40,
and inherited arithmetic, cleanup and physical-RNG phase controls pass.
This transfers an existing construction; it is not a novelty or full record.
All17 protected files remain unchanged. The19-member archive verifies locally.

The conservative equal-word integration plan is deprioritized. Triangle bounds
over unrestricted q/e controls reach502-bit words at illustrative horizon138.
The137 ordinary forward components excluding the exceptional first tick cost
160068 CCX analytically, or320136 with their inverse, already exceeding a raw
payload pass182507/186736. The two coefficient words alone use1004 wires,
before live coordinates, rails, tape and scratch. Endpoint, normalization,
coordinate multiplication and cleanup are still omitted. Horizon138 is not
a convergence proof or a permitted iteration cut. These are partial analytic
costs of one conservative plan, not lower bounds on all cofactor algorithms.
A tighter proved reachable-state bound or a different representation remains open.
'''}
for name,body in reports.items():
    (root/'experiments'/name/'STATUS.md').write_text(body,encoding='utf8',newline='\n')
sgt=stamp.astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: direct payload costs and cofactor budget

No new complete resource record. Fresh1685-submission snapshot at23:06UTC
keeps product d9ae2845 at Q1234/T761077/product939169018 and Toffoli752991
atQ1863. The public width minimum is now672 (5764884a/sourcebcbe0b65).
Earlier snapshots and all gate verdicts remain unchanged.

Raw subphase observer/refinement completed0. Its overlapping pacc labels are
not pure gate families; use the new byte-identical direct-membership profile.
All512 rows match the unchanged raw circuit and eight scalar controls pass.
Payload costs182507/186736 diagnostic Toffolis for divide/multiply, including
51952/52334 in actual rotations. These raw observations are not scored results.
Legacy51/direct26-member archives verify locally; all17 protected files match.

Cofactor rotation transfer passes8 unique native tests:16-bit component86 CCX
versus93, with8160 small-word cases and full RNG phase controls. Its19-member
evidence verifies. Conservative unrestricted-control equal-word storage still
costs320136 ordinary cofactor CCX including inverse at illustrative138 ticks,
with1004 coefficient wires alone. First exception, normalization, endpoints,
coordinate multiplication and cleanup remain omitted. This specific plan is
deprioritized; these are analytic partial budgets, not universal lower bounds
or a new convergence schedule. No empirical maximum becomes a circuit cut.

Next native component: breakthrough-parity-bridge-20261020, supervisor2342842,
source-exclusive pivots for mixed Cuccaro/Gidney parity adders. Check run.exit,
preserve failed tests, then assess availability at real tight source sites.
No point-add integration or score yet; future ready submissions queue.
Run log: experiments/autorun-20261020-breakthrough/LOG.md.

'''
patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
    p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1)
    updated=first+'\n\n'+prefix+rest.lstrip('\n')
    patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    raw=p.read_bytes();first,rest=raw.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
    if rest.startswith(ending):rest=rest[len(ending):]
    p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-domain-index.patch').write_text(''.join(patch),encoding='utf8',newline='\n')
with(r/'LOG.md').open('a',encoding='utf8')as f:
    f.write(f'\n- {stamp.isoformat()}: direct profile and cofactor rotation/budget cycle saved. All51/26/19 archived members verified locally; component8 unique controls PASS. Conservative cofactor plan deprioritized. New native parity bridge2342842 active. Fresh public width672, product939169018 unchanged. No new complete candidate/gate/nonce/score.\n')
print('Additive checkpoint prepared; preserve all existing document bodies.')
