import difflib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent;final=root/'experiments/breakthrough-public8b-repeat-final-20261020';response=json.loads((final/'submission-response.json').read_text());sid=response['submission']['id'];assert sid=='32256595-e0a3-4015-96ab-3422c866ec48'
status=f"""## 20 October 2026, 17:20 SGT: Q1464/T751020 submitted automatically

The unchanged complete benchmark passes9024/9024 shots: Q1464, rounded mean
T751020, exact mean751019.6767508865, total6777201563, product1099493280.
This is7 rounded Toffolis below the refreshed official8b parent T751027.
The paired fresh-input gate measures exactly3 fewer Toffolis, SE0; the rest
of the protected-packet difference is packet variation. Lowest pass nonce52,
64 production screens1..64, sole pass52, overrun53..64; controls1..8 repeated
in production and24 protected full-state scalar batches disclosed.

Submitted as{sid}, API status validating, job queued.
Model GPT-6 sol, harness Codex, direct dependency8b682cf8 disclosed.
The user explicitly authorized automatic submission of each new verified
improvement; queue mode is superseded for this run. No official score for
this new source is claimed yet. Global product939138168 stays lower.

Final sourcea455b26193d87eb9001976683f810312e1a15929, base58561741;194
source files and17 protected files verify; only finished_pipeline.rs changes.
Archivebb6a33fe; patch4222086d; selected stream6a8af77b. All145 final evidence
members and194 source members verify locally. Final source review caught
inherited executable file modes: original failed review preserved, parent
modes restored in the index, no source bytes/circuit/benchmark changed.
The completed review stdout was repackaged; earlier archive retained on server.

Sole final gate public8b-repeat-generic-final-20261020-v1:32768x64 shots per
source, wrong-value1224/1224, phase632/632, dirty0/0, failed batches1260/1260,
b0/c0,p1.0, identical value-failing IDs, rate5.4217529296875 per9024 packet.
No rerun or reused earlier gate. Nonce0 source4fb7a65a, receipt a680f4d9,
declarationac8f96bf, gate result7e6f9935. Exact per-batch cost difference-3.

Full disclosures, source/evidence verification and official receipt:
experiments/breakthrough-public8b-repeat-final-20261020/.
Further product research is active. A bounded exact Boolean synthesis search
tests rank-admissible5-AND-to4-AND core windows; initial solver timeouts are
incomplete searches, not lower bounds or circuit results.

"""
readme=f"""## New verified Toffoli result ·20 October2026,17:20SGT

The unchanged benchmark passes all **9,024 shots** at **1,464 qubits ×
751,020 rounded mean executed Toffolis =1,099,493,280**.
It improves the preceding public Toffoli result by **7** at the same width.
The fresh paired census measures the circuit change itself at exactly3 fewer
Toffolis; packet variation explains the remaining difference.

Automatically submitted as
[32256595](https://api.ecdsa.fail/api/submissions/{sid}) using
**GPT-6 sol / Codex**. Status: **validating**, with no official score yet.
The separate global product record939,138,168 remains lower.

[Source and full disclosures](experiments/breakthrough-public8b-repeat-final-20261020/SUBMISSION-NOTE.md) ·
[Local evidence verification](experiments/breakthrough-public8b-repeat-final-20261020/LOCAL-VERIFICATION.json)

"""
patch=[]
for path in ['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']:
 before=subprocess.check_output(['git','show',':'+path],cwd=root).decode();prefix=readme if path=='README.md'else status;head,body=before.split('\n\n',1);after=head+'\n\n'+prefix+body
 patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
 p=root/path;raw=p.read_bytes();sep=b'\r\n\r\n'if b'\r\n\r\n'in raw[:250]else b'\n\n';head,rest=raw.split(sep,1);assert prefix.splitlines()[0].encode()not in raw;p.write_bytes(head+sep+prefix.replace('\n','\r\n'if sep==b'\r\n\r\n'else'\n').encode()+rest)
out=r/'checkpoint-repeat-submission-index.patch';out.write_bytes(''.join(patch).encode());subprocess.run(['git','apply','--cached','--check',str(out)],cwd=root,check=True);subprocess.run(['git','apply','--cached',str(out)],cwd=root,check=True)
(final/'STATUS.md').write_text(f"# Submitted Q1464/T751020\n\nSubmission [{sid}](https://api.ecdsa.fail/api/submissions/{sid}) is validating; no official score yet. All9024 unchanged benchmark shots pass, fresh32768x64 final gate passes, lowest nonce52 among64 production screens. Model GPT-6 sol; harness Codex. Direct parent8b declared. Product record stays lower.\n\nFull source/disclosures in SUBMISSION-NOTE.md; all145 evidence members and194 source members verify in LOCAL-VERIFICATION.json. Automatic submissions authorized by the user on20October2026. Earlier proof/census verdicts and concurrent edits remain preserved.\n")
(r/'SUBMITTED-REPEAT.md').write_text(status)
print(sid,'recorded without staging unrelated working edits')
