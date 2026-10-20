"""Add this cycle only; retain every pre-existing documentation edit."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
sgt=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: native eleven-helper compression and complete forward fold validated

No new scored result, final statistical gate or nonce search. Public refresh
03:16:55UTC remains1687 entries, product54fc Q1234/T761052/product939138168,
width671, T752991. Queue mode and every earlier gate verdict remain.

The active31-helper core can be converted by an invertible affine change
into20 required forms plus11 temporary functions. All11 are HMR-erased with
Clifford phase repair and regenerated with11 ANDs. Two exhaustive native
tests and original-prefix control pass all16384 source assignments, mixed
guards, measurement coefficients, allocation reuse and uninterrupted replay.
Earlier32-AND reconstruction also passes. Compiler and guarded fixture
failures remain: segmented Simulator.apply_iter calls reset the local guard
stack; corrected fixture restores it and checks uninterrupted execution.
All67 native evidence members verify locally, including all five source
revisions. This is a component storage result, not a scored point-add record.

Complete forward-fold integration passes one exhaustive test plus19 retained
controls: five tight budgets, two TT modes, three guards, full small inputs,
independent upper words and all measurement/reset positions. New cap1233
matches old outputs, phase and cleanup. Complete raw stream6b375c3a has
Q1233, builderexpected764011.8;22 production calls borrow all11 helpers.

Selected loans borrow only enough helpers to leave10 ladder carries. Same20
native controls pass. Complete raw5bbda387 remainsQ1233, expected763932.2,
79.6 below full borrowing and39.6 below reserve-only. Originalcap1234 stays
byte-exact13f6. These raw diagnostics precede postpasses and remain too
costly for a product record; no full benchmark or failure census is claimed.

Global planner cap1233 failed its existing capacity assertion at forward130:
room15 versus modeledfoldneed36, shed pool14 plus2 tops and4 internal wires.
The assertion is preserved. New preflight experiment uses the independently
proved peak=max31 prefix helpers, retained helpers plus10 carries, only
supported forward fin0/mw56 contexts, with original m0 erase budget intact.
It extends native tests to before-ladder room0..4 versus an unconstrained
reference before full generation. Initial fixture type error is preserved;
test-onlyv2 is active. No arithmetic cuts, windows or iterations are changed.

Cleanup-only models can erase13 of the20 retained forms for free but leave
seven unresolved. The recorded greedy auxiliary searches also stall; these
are finite negative models, not lower bounds. Native erasure, complete fold,
selected-loan and failed-global archives all verify locally. Their bundles
now retain every native evidence member, including generation/failure logs.
Protected17 and pre-existing user edits remain unchanged.

Checkpoint12a4e198 is pushed and remote-verified. Its push was initially
rejected by auto-review as unverified export; read-only checks confirmed
public MonitSharma/elliptic_curve_dsa, prior remote69e5, explicit repository
push instructions and no credential/resource-preflight artifacts. Same push
then passed review. No action remains blocked by that rejection.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();patch=[]
for name in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);updated=first+'\n\n'+prefix+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name));data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-core-loan-index.patch').write_bytes(''.join(patch).encode())
for name in ['DEVELOPMENT-NOTES.md','LOG.md']:
 p=r/name;p.write_bytes(p.read_bytes().rstrip()+b'\n\n'+prefix.rstrip().encode()+b'\n')
print('Owned additive native-core checkpoint prepared.')
