"""Stage an additive research checkpoint without staging pre-existing docs edits."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc);sgt=stamp.astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: cleanup-aware carry components; public parent refreshed

No new scored result, final statistical gate or nonce search. Fresh public
snapshot01:42:03UTC/09:42SGT has1687 entries: product54fc4f25 at
Q1234/T761052/product939138168, width671, T752991 unchanged. Its exact source
3dee0cd6 reproduces published stream51671a28; all source archive bytes and
17 protected files verify locally. Historical d9ae remains our accepted result.
Future gates use the current public record's exact stream. Queue mode stays.

Native phase predicates pass3 tests: early nonadjacent carry erasure needs
no target sums; two-stage repair on original data plus fused top phase uses
n-2-d carries. Exact phase, guards, all small schedules, RNG positions,
double application, width/draw/Stats controls pass. This is a component result.

Weighted native planner initially failed11>8 because it omitted boundary
cleanup space. Corrected9/10 family passes3 tests; test-onlyv4 covers all
measurement positions including inverse. Cleanup-aware planner with the new
predicate now passes3+3 tests,983040 full case/configurations, old8/9 and
actual core rows, plus inverse/measurement controls. It admits8/9/10 carry
budgets in this family. No7 schedule or general lower bound follows.
Fixture-only independent SHAKE measurement-word cost control is active;
earlier correlated deterministic-word means are not unbiased cost estimates.

Source-local oldplan8->validatedplan7 completes raw0bd52235 but stillactual
Q1234 at squareop5834221, builderexpected763838.2 diagnostic. Paired512x64
rawT+1604.70(SE4.34), same50 value-failing shot IDs, dirty0, other registers
equal. Full-output equality FAILED on target lanes already value-failing in
both; phase50/38, failed batches66/59. Cause unisolated; preserve verdict.
No complete resource improvement. Earlier launcher permission failure and
identical repeated baseline control are preserved separately.

Metadata-only square audit exactly reproduces both13f6 and0bd complete
streams. The remaining peak is a128-bit modular call, active1108, with
known_terminalSome: a proved constant OUTPUT, implemented by measuring and
forcing the old top bit. Next adapter must preserve that exact reset/phase
channel, including promise-violating inputs, rather than replace it with a
full adder. Detailed semantic measurement-alignment tests are planned in
experiments/autorun-20261020-breakthrough/DEVELOPMENT-NOTES.md.

Ten newer source/test bundles and the40-member negative replay archive
verify locally. Failed preparation/compiler/width/output outcomes remain.
All17 protected files unchanged. Existing user edits and Q692 evidence stay.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);assert prefix.split('\n')[0]not in head
 updated=first+'\n\n'+prefix+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-cleanup-index.patch').write_text(''.join(patch),encoding='utf8',newline='\n')
print('Prepared owned additive docs patch; preserved pre-existing working edits.')
