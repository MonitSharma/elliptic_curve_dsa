"""Add only this cycle's research summary to the index; preserve user edits."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
sgt=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: complete raw Q1233 prototype; active-core workspace research

No new scored result, final gate or nonce search. Public refresh03:16:55UTC
has1687 entries; product54fc remains Q1234/T761052/product939138168, width671,
Toffolis752991. Historical d9ae remains our accepted submission; queue mode
and every earlier gate verdict remain unchanged.

Exact terminal-output reset/phase adapter passes7 focused native tests.
Its integration clears the square peak. Direct phase-transport controls pass
18 native tests and clear the next multiply peak. A long-lived T0 phase
temporary remains; a lifetime-aware direct cubic replacement passes19 tests
and generates a complete raw circuit at peak/touchedQ1233, stream8447753a.
Raw builderexpected763971.8 versus762230.8 control is noncompetitive in cost;
neither these construction diagnostics nor component counts are scored results.
Controlcap1234 stays byte-exact13f6. All17 protected files stay unchanged.

Immediate-allocation cubic policy and narrow C3 budget policy pass their
components but do not activate in the full circuit; exact activation traces
explain why. Failed compiler/preparation/launcher/width fixtures are retained.
Eight new native evidence archives and exact source/test bundles verify locally.

The exact18-product synthesis found for old19-product addend_from_n is an
INACTIVE legacy-helper result. Enabled forward/reverse tables have14/12
products. Earlier weighted fixtures called actualcore also used that legacy
helper and demonstrate no active-production gain. Their old evidence remains.

The active prefix independently matches all31 helper/21 field/8 derived-bit
functions on all16384 independent source assignments. Its original frame has
rank46 and no simple linear spare. After writing six low sums, new exact
models expose20 required helper forms and11 garbage forms. All11 can be
HMR-erased with Clifford phase repair and regenerated with11 ANDs (earlier
generic32-product reconstruction preserved). Native implementation is under
validation. Initial compiler and guarded fixture failures remain; diagnosis
found Simulator.apply_iter resets its local guard stack between segmented
calls. Corrected fixture adds an uninterrupted full-stream control. No native
or full-fold workspace improvement is yet claimed for this new technique.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();patch=[]
for name in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);updated=first+'\n\n'+prefix+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-workspace-index.patch').write_bytes(''.join(patch).encode())
for name in ['DEVELOPMENT-NOTES.md','LOG.md']:
 p=r/name
 with p.open('ab')as out:out.write(('\n'+prefix).encode())
print('Prepared additive checkpoint; pre-existing working edits preserved.')
