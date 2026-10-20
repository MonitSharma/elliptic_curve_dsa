"""Stage only the additive research update, preserving unrelated working edits."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
sgt=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
prefix=f'''## {sgt}: complete raw Q1232; replay-boundary scope corrected

No new scored result, final statistical gate or nonce search. Public snapshot
04:00:26UTC has1687 entries; product54fc Q1234/T761052/product939138168,
width671, Toffolis752991. Our accepted d9ae and every earlier verdict stay.

Preflight v2 passes20 native controls and generates rawQ1233/763010.2.
Sharing the immutable phase/fold letter product passes21 controls, removes
128 raw expected Toffolis, and generatesQ1233/762882.25, stream8d458cf4.
Fin1 prefix compression passes4 controls:30 helpers become20 retained forms,
10 erasures and11-AND regeneration. Complete fin1 fold passes22 controls,
butQ1232 generation fails reverse126. Exact seven-carry schedule clears126
then fails125;24 native executions cover23 unique tests, with filter overlap
disclosed. Expanded reverse budgets7/8/9 pass23 native tests and complete
rawQ1232/763623.1, stream23acf8d4. Control1234 remains exact13f6ffc3.

Scope correction: direct cut/profile constants stayed fixed, but the global
budget changes derived replay chunk boundaries. Metadata-only audit exactly
reproduces all three streams; recorded site counts2213/2255/2297 and site
multisets differ. Earlier broad claims of unchanged arithmetic windows or
predicates were unsupported. Component phase/value equivalence remains
valid; full point-add equivalence is not established. A predeclared512x64
development comparison now tests the frozen raw streams with full output,
phase, cleanup and protected scalar controls. This is not a final gate.

Generic stream-derived passes exactly reproduce the official baseline when
the original full pipeline is selected. Generic mode omits source-bound
certificates, census cuts and nonce tail: diagnostic weights761696.25 control
and762347.25 Q1233 are noncompetitive. Diagnostic zstd framing differs from
official framing; original assertion failure is retained and full raw
operation-record hashes verify equality. No source or binary was changed
to recover that control.

Fourteen-variable Boolean optimizer passes10 native tests, exhaustive bit
maps/scalar references and48 guarded measurement circuits across1024 inputs.
It saves only2 diagnostic Toffolis on the frozen generic candidate. A new
exact sparse Boolean-polynomial engine passes3 native controls and is being
audited on that frozen stream; no expected gain is counted as a result.

Eight completed native archives now verify every member locally; source,
patches, all17 protected-file checks, logs, negative outcomes and differing
replay traces are preserved. Latest public snapshot is sealed independently.
Protected harness/curve/simulator/Cargo/toolchain and user edits stay intact.

'''
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();patch=[]
for name in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);updated=first+'\n\n'+prefix+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name));data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-width-index.patch').write_bytes(''.join(patch).encode())
for name in ['DEVELOPMENT-NOTES.md','LOG.md']:
 p=r/name;p.write_bytes(p.read_bytes().rstrip()+b'\n\n'+prefix.rstrip().encode()+b'\n')
for name in ['breakthrough-sparse-polynomial-20261020','breakthrough-width-correctness-20261020']:
 p=root/'experiments'/name;(p/'.gitattributes').write_bytes(b'* -text\n');(p/'.gitignore').write_bytes(b'/tool/\n/evidence.tar.gz\n')
print('Owned additive width checkpoint prepared.')
