"""Add only this research checkpoint; preserve all pre-existing user edits."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent;stamp=datetime.now(timezone.utc);sgt=stamp.astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: exact phase-pebble components; modular integration active

No new complete scored result, final statistical gate or nonce search.
Official d9ae2845 remains Q1234/T761077/product939169018. Fresh public snapshot
00:17:24UTC/08:17SGT,1685 submissions: product unchanged, width672, T752991
atQ1863. Future submissions remain queued; all old verdicts stand.

Early carry erasure/regeneration passes3 native tests. Its direct phase
replacement passes3 tests and saves d clean carries at expected0.5/1 added
scoredT per drop, with unchanged HMR count. General arbitrary-schedule,
carry-birth phase-hook and paused-sum contracts pass3 tests, including3325952
declared small-basis/parameter evaluations plus all physical RNG coefficients
and inverse. Paused None views indicate an already-completed target sum;
consumers must honor that frame and restore all data they touch.

Fresh accepted-source integration (not the older negative branch) passes
3+1+4 native controls. Original1234 exact13f6; hard1233 remainsactual1234 at
a127-carry modular ripple, raw17324474, builderexpected762841.2 (+610.4 raw
diagnostic). No generated count is a score. Zero-input-carry adapter passes3
tests, then fixture-onlyv2 adds fully enabled exhaustive cases to mixed guards
with unchanged runtime bytes. It preserves the ordinary adder CCX/HMR base.

Active: breakthrough-phase-pebble-modular-20261020 supervisor2435977.
Optional carry and exact leading-zero trim/hook offsets, full plain modular
ripples and pure square chunks; copy/deferred/known-output/known-terminal/
external-carry contracts remain excluded. Original outer planners/windows/
iterations fixed. Native3+1+4+3 controls before1234/1233 generation; require
1234 exact13f6 and inspect actual peak/touched IDs before further replay.

Earlier local-fold932f5184 remains noncompetitive actualQ1234. Paired512x64
T+1430.82;48 identical value-failing shot identities, dirty0. Full four-register
equality FAILED in11 batches. Same-input v2 observation reproduces every old
field/hash and identifies11 target lanes already failing in both sources;
other registers match. Cause unresolved; preserve the failed equivalence
verdict and never claim equality on inherited failing inputs.

Construction-only fold ownership preserves full13f6 and failed-prefix66ba9d6c.
The t68 allocation is ordinary Y15 ladder_d, not a fixed core AND;12 generic
54-bit folds peak1234/lowcar0. Core truth audit:19CCX, all computed functions
independent, output nonlinear dimension16; native78 promised inputs pass.
Unsupported n=-128 differs from the multiplication reference. No simple
redundant-AND removal or general circuit lower bound follows.

Seven later native archives33/26/16/20/17/35/34 members verify locally;
output audit72 also verifies. Exact source/test bundles preserve patches and
native line endings. All17 protected files unchanged. Primary measurement-
pebbling literature recorded; no novelty or transferred percentage claim.
Next cost direction is weighted chunk planning with exact phase-drop ranks;
uniform-rank50-bit budgets are analytic only, not installed native records.
Details: experiments/autorun-20261020-breakthrough/DEVELOPMENT-NOTES.md
and LOG.md. Preserve pre-existing user edits and Q692 evidence.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);assert prefix.split('\n')[0]not in head
 updated=first+'\n\n'+prefix+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-pebble-index.patch').write_text(''.join(patch),encoding='utf8',newline='\n')
with(r/'LOG.md').open('a',encoding='utf8')as f:f.write(f'\n- {stamp.isoformat()}: phase-pebble checkpoint; native component/source evidence sealed, failed full-equivalence result preserved; modular2435977 active, no final gate/nonce. Existing user edits remain separate.\n')
print('Additive checkpoint and index patch saved.')
