"""Add only this checkpoint to index; preserve existing working document edits."""
import difflib,hashlib,json,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc);sgt=stamp.astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: exact phase fusion and independent carry limit

No new complete resource result, final statistical gate or nonce search.
Official parent d9ae2845 remains Q1234/T761077/product939169018. All old
verdicts and the accepted source remain unchanged; future submissions queue.

Global-cap plan7/square refinements finally generate actual1233/touched1233
with short zero-extended sources, rawb3a3d124. Paired512x64 diagnostic keeps
the same54 value-failing shot identities and zero dirty, but adds738.28 rawT
(SE4.49), exceeding the approximate617-T budget per saved qubit. This is a
development width control, not a scored improvement. Earlier square/ripple
peaks remained1234; their evidence and outcomes are preserved.

Exact two-stage carry-phase component passes4 native tests:262144 pair and
174592 ladder bases, exact signs/operand restoration/measurement coefficients.
Source-row rank<=1 saves one clean carry at zero added scoredT, rank2 at+1T.
CCZ is scored and attributed. Seven local Boolean identities UNSAT, wrong
sign control SAT. Separate source-borrowed predicate passes3 native tests.
Six terminal archives30/46/45/32/37/25 members verify locally;17 protected
files unchanged. These are components/development evidence, not records.

Byte-identical original13f6 source audit finds735 eligible phase predicates;
392 rank1, all8 that reach1234 rank1. Real allocation-array calls resolve
mostly to modular ripples; shared fold carries and two Y15 core sites remain
separate constraints. Do not infer a global saving from a component.

Active: breakthrough-hardcarry-20261020 runner-v2 supervisor2390788. Keep all
original planner caps1234 and impose separate hardcarry1233. Exact plain
borrowing, unique bridge pivots, square adapters and tight phase fusion;
phase-only YP8 r2/r3 temporary AND consumers become scoredCCZ. Pending hooks
and paused callbacks remain excluded. Initial parity5/phase4 tests pass;
fold fixture101 was missing HARD_CARRY_CAP because fixtures bypass build.
Runner-v2 supplies1234 to fixtures; frozen runtime bytes remain unchanged.
Check run-v2.exit, native controls and ADMISSION-RESULT before any replay.
Declared baseline1234 must exactly match13f6. No final gate/nonce yet.
Run log: experiments/autorun-20261020-breakthrough/LOG.md.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip()
patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1)
 assert prefix.split('\n')[0]not in head
 updated=first+'\n\n'+prefix+rest.lstrip('\n')
 patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-phase-index.patch').write_text(''.join(patch),encoding='utf8',newline='\n')
family=root/'experiments/breakthrough-fold-plan7-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(family/'PLAN-FAMILY-ANALYSIS-MANIFEST.json').write_text(json.dumps({'created_at_utc':stamp.isoformat(),'files':{n:sha(family/n)for n in['enumerate-family.py','PLAN-FAMILY-ENUMERATION.json']},'scope':'Additive post-seal analytic enumeration; original39-member native archive remains unchanged. Bounds concern only the specified nonadjacent-drop family and generic carry-stage model.'},indent=2)+'\n')
with(r/'LOG.md').open('a',encoding='utf8')as f:f.write(f'\n- {stamp.isoformat()}: phase/square checkpoint; six terminal archives locally verified, original-planner hardcarry runner-v2 active2390788, no final gate/nonce. Preserve all original user edits.\n')
print('Additive phase checkpoint saved; apply only the prepared index patch.')
