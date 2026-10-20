import difflib,json,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip();v=json.loads((root/'experiments/breakthrough-public140-exact154-final-20261020/LOCAL-VERIFICATION.json').read_bytes());assert v['source_revision']=='1b550a0165a4578b041cebb5c2655f0a8a6cf844';sgt=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
readme=f'''## Complete local Toffoli improvement · {sgt}

The unchanged benchmark passes all **9,024 shots** at **1,464 qubits ×
751,027 rounded mean executed Toffolis = 1,099,503,528**. This locally verified
candidate is **queued, not officially evaluated**. It saves **155 Toffolis
at the same width** versus the current public Toffoli leader,
[4045a75a](https://api.ecdsa.fail/api/submissions/4045a75a-32a0-4d3c-b7ca-03b51dc12b25),
which officially reproduced our preceding Q1464/T751182 result. Public records
were refreshed at07:20 UTC. The independent global product939,138,168 stays lower.

This new frozen circuit passed its own declared2,097,152-shot-per-source
gate. Value-failing shot IDs match its parent; dirty shots0. Failed batches
are1200 versus1193; paired exact p0.162 meets the declared standard. Lowest
passing nonce209,256 production screens, additional controls1..8 and overrun
210..256 are disclosed. Source1b550a01; AI research attribution GPT-6 sol/Codex.
Approximate arithmetic remains; finite-packet success is not universal correctness.

[Complete disclosures](experiments/breakthrough-public140-exact154-final-20261020/SUBMISSION-NOTE.md) ·
[Independent local verification](experiments/breakthrough-public140-exact154-final-20261020/LOCAL-VERIFICATION.json) ·
[Full source and evidence](experiments/breakthrough-public140-exact154-final-20261020/final-evidence.tar.gz)

'''
prefix=f'''## {sgt}: Q1464/T751027 complete local pass; native prefix27/full-fold work

New complete unchanged benchmark: all9024 shots pass, Q1464, rounded mean
T751027, exact mean751027.0876551418, total6777268439, product1099503528.
Source1b550a0165a4578b041cebb5c2655f0a8a6cf844, stream77d43b25. All194 source
members and117 final evidence members verify locally. Queue mode, no new
upload. The preceding Q1464/T751182 result is now officially scored as4045a75a,
public sourced45e76b3. API rejected only because product did not improve the
incumbent; it remains the public T minimum. Public source193 files and17
protected files match the previously validated locala70d1cb6 byte-for-byte.
Fresh07:20:10UTC snapshot1690: T751182/Q1464, product939138168 atQ1234/T761052,
width671. New local saves155 at unchanged width, not the global product record.
The original queue/freeze receipts remain dated history; the concurrently
edited old submission note is preserved separately from this checkpoint.

Independent exact154 final gate: declared06:54:07.721292UTC, label
public140-exact154-final-20261020-v1,32768x64 shots/source versus exact current
official4045 streamdc621004. Frozen nonce0candidate7b165a67. Wrong-value shots
1162/1162, identical failing shot IDs; phase668/634, dirty0/0; failed batches
1193/1200. Candidate5.163574failed batches/packet. Paired b22/c15, exact
one-sided McNemar p0.1620043000439182. All four criteria pass; the seven extra
failed batches are disclosed. No rerun/relabel/extension/re-judging. Previous
uniform2 gate was not reused for this independent circuit.

Ascending nonce1..256: sole pass and lowest209; overrun210..256. Additional
partial-packet controls1..8 repeat production and compare24 protected full
qubit/classical/phase/RNG states plus curve/partial-mask checks. Selected full
protected packet and unchanged benchmark both pass. Only the nonce literal
changes after the gate, every pre-tail record matches, all17 protected files
and historical results remain intact. GPT-6 sol/Codex research attribution.

Exact lease discovery on public140 accepts154 arbitrary-cut proofs. Budgets16
and64 generate identical output with no referenced width increase. Dependency
pruning agrees exactly but does not speed the audit materially. Its first test
wrongly expected an incomplete SymTriple algebra to prove a guarded identity;
the full reference also rejects it. Failed fixture/source and corrected7 native
controls are preserved. Initial native exact154 research runner compared zstd
frames incorrectly. Diagnostic window27 differs from the protected writer;
every uncompressed record matches. Original assertion failure retained, source
and generation unchanged,27 controls pass. Complete benchmark is the result.

Structural native result, separate from scored results: original31-helper
prefix becomes peak27/final20 with the same31 ANDs,11 HMRs and Clifford phase
repair. Protecting C1..C4 and TT until ordered cleanup removes the earlier
one-cubic obstruction. Exact14-input models and generated716-CNOT basis
schedule pass native16384 inputs,3 guards,15 measurement modes plus original
control and missing-phase fault detection. Cleanup restores low sums in place
with13 ANDs/31 HMRs (44 total core ANDs, versus42 for earlier loan construction).
All42 independent measurement coefficients and guards pass. Complete forward
fold matches the unmodified reference on six rooms28/29/30/31/33/35, all16384
core assignments and independent upper words; no point-add record is claimed.
The first quartic and alternative-basis models remain negative finite searches,
not lower bounds. Metadata alias/list correction preserves original reports.

Production integration passes29 native controls. Original hard1234 control is
byte-exact13f6; raw hard1233 stream8e0d9a6f has diagnostic763799.2 and hard1232
stream2e07eb5a has765396.1, both too costly. Hard1231 is rejected by the unchanged
research parameter whitelist before circuit generation, not an arithmetic
capacity verdict. A fixed new grid tests using this workspace at original
global1234 width, with preflight minima28/29/30, to reduce surrounding carry
shedding. No packet data or nonce enters any structural experiment. Preserve
Q692 and all earlier failed-gate verdicts. The active substantial product
objective remains unfinished; unrelated user edits and server jobs stay intact.

'''
patch=[]
for name,addition in [('README.md',readme)]+[(n,prefix)for n in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']]:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1);updated=first+'\n\n'+addition+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name));data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+addition.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-exact154-index.patch').write_bytes(''.join(patch).encode())
for name in ['LOG.md','DEVELOPMENT-NOTES.md']:
 p=r/name;p.write_bytes(p.read_bytes().rstrip()+b'\n\n'+prefix.encode())
p=r/'READY.md';p.write_bytes(('''# Latest queued local result: Q1464 / T751027

Source1b550a0165a4578b041cebb5c2655f0a8a6cf844, nonce209,256 screens.
Complete unchanged benchmark9024/9024; independent final gate PASS.
Public07:20 refresh Tparent4045 is Q1464/T751182. New candidate improves155
at identical width. No upload or official evaluation for this candidate.
Queue mode; refresh before submission. Full note/source/evidence:
`experiments/breakthrough-public140-exact154-final-20261020/`.
Server candidate:
`/home/hclau/ecdsa_research/breakthrough-public140-exact154-final-20261020/candidate`.
AI research attribution GPT-6 sol; harness Codex. Global product stays lower.
Continue product work. The older queue entry below is historical: it became
official submission4045a75a-32a0-4d3c-b7ca-03b51dc12b25.

''').encode()+p.read_bytes())
print('Owned exact154 and native-prefix checkpoint prepared.')
