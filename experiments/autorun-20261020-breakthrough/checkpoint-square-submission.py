"""Stage additive result notices while preserving unrelated document edits."""
import difflib,json,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
ws=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent;final=ws/'experiments/breakthrough-public322-square-final-20261020'
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ws).strip()
b=json.loads((final/'BENCHMARK-RESULT.json').read_text());v=json.loads((final/'FINAL-VERIFICATION.json').read_text());local=json.loads((final/'LOCAL-VERIFICATION.json').read_text());sid=json.loads((final/'submission-response.json').read_text())['submission']['id'];assert sid=='a4ee760a-0500-4d54-9822-4a3c56806fd5'and b['rounded_mean_executed_toffoli']==750911 and local['source_files']==196 and local['members']==238
sgt=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
readme=f'''## New complete Toffoli result · {sgt}

The unchanged benchmark passes all **9,024 shots** at **1,464 qubits ×
750,911 rounded mean executed Toffolis = 1,099,333,704**: **109 fewer
Toffolis at the same width** than the preceding official T751020 result.
Automatically submitted as
[a4ee760a](https://api.ecdsa.fail/api/submissions/{sid}) using
**GPT-6 sol / Codex**. Official evaluation is pending at this checkpoint.
The separate global product record 939,138,168 remains lower.

[Source and disclosures](experiments/breakthrough-public322-square-final-20261020/SUBMISSION-NOTE.md) ·
[Complete local verification](experiments/breakthrough-public322-square-final-20261020/LOCAL-VERIFICATION.json)

'''
detail=f'''## {sgt}: Q1464/T750911 verified and automatically submitted

Complete unchanged benchmark: 9024/9024 shots, Q1464, rounded mean T750911,
exact mean750910.5620567376, total6776216912, product1099333704. Saves109
rounded Toffolis at unchanged width versus direct official parent32256595,
public source63d63c90. Submission {sid}, GPT-6 sol/Codex,
currently validating. No official score yet; global product939138168 is lower.

Final source28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f,196 point-add files,
17 protected files. Only mod.rs and two new modules differ. Exact square
workspace1234->1408; raw structural grid chooses smallest byte-identical tie.
Unchanged generic passes, independently proved153 unconditional product
leases, full native rewrite canonical assertion, second generic pass.
Native27 controls pass. No arithmetic/precision/public row/correctness cuts.
Archive sourceee0ee69c, patch9e3c25de, selected stream54c8cd60. All238 final
evidence members and196 source files verify locally; original full archive
499882f3 retained. Completed review output preserved separately as
source-review-completed.log; archive captured the earlier in-progress log.

Own sole final gate public322-square1408-final-20261020-v1, declared
10:19:22.615442UTC before32768x64 fresh shots/source, nonce0. Exact parent
stream6a8af77b; candidate807cc252. Wrong-value1104/1104 with identical shot
IDs, phase622/594, dirty0/0, failed batches1160/1145, candidate4.9269104 per
9024-shot packet. b12/c27, one-sided exact McNemar p0.99526235, paired mean
difference-108.82871437 with SE0.26991412. All four criteria pass. Declaration
90c480e8, result88c5b918. No reused gate, relabel, extension or rerun.
Lowest passing nonce8,64 production screens1..64, sole pass8, overrun9..64;
eight extra partial controls and24 protected full-state/RNG/curve batches,
selected9024-attempt packet pass. Every pre-tail record matches frozen source.

Independent larger-product research: exact quadratic-span closure excludes
all63 original-span retained interfaces, independently reproduced by full
augmented-column intersection and dimension formula. This excludes<=30 AND
programs only when all intermediate functions stay in the original46-function
span; not an unrestricted circuit bound. All88 fresh primary-pair quadratic
auxiliaries across651 interfaces each are negative in the declared extended
language. Raw capacity grid1536..2560 yields identical streams in all8 cases.
Every corresponding archive member verifies locally. No model/proxy is scored.
Active full generic comparison of baseline versus compact prefix27/cleanup11,
Q1234, tests whether pass interactions offset its raw+51.75 cost. It remains
research only. PreserveQ692, all past failed gates and unrelated jobs/edits.

Source/evidence/official receipts: experiments/breakthrough-public322-square-final-20261020/.
Automatic verified-result submissions remain authorized. Continue the substantial
product objective; do not mark the active goal complete on the T result alone.

'''
patch=[]
for name,addition in [('README.md',readme)]+[(n,detail)for n in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']]:
 head=subprocess.check_output(['git','show','HEAD:'+name],cwd=ws).decode();first,rest=head.split('\n',1);updated=first+'\n\n'+addition+rest.lstrip('\n');patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name));p=ws/name;data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+addition.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-square-submission-index.patch').write_bytes(''.join(patch).encode())
subprocess.run(['git','apply','--cached',str(r/'checkpoint-square-submission-index.patch')],cwd=ws,check=True)
(r/'LOG.md').write_bytes((r/'LOG.md').read_bytes().rstrip()+b'\n\n'+detail.encode())
extra=['experiments/breakthrough-public322-square-final-20261020','experiments/breakthrough-public322-capacity-grid-20261020','experiments/breakthrough-prefix-fresh-aux-20261020','experiments/breakthrough-prefix27-generic-interaction-20261020']
for name in extra:
 p=ws/name;(p/'.gitattributes').write_bytes(b'* -text\n');q=p/'.gitignore';data=q.read_text()if q.exists()else''
 for line in ['candidate/','observer/','tool/','target/','__pycache__/','evidence.tar.gz','*resource-preflight*','public-before-upload.json']:
  if line not in data.splitlines():data+=line+'\n'
 q.write_text(data)
extra+=['experiments/autorun-20261020-breakthrough/'+p for p in ['collect-square-final.py','collect-capacity-aux.py','collect-capacity-aux-base.py','seal-capacity-aux.py','checkpoint-square-submission.py','checkpoint-square-submission-index.patch']]
subprocess.run(['git','add','--']+extra,cwd=ws,check=True)
allowed=extra+['README.md','docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md'];staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ws).decode().splitlines();assert all(any(p==a or p.startswith(a.rstrip('/')+'/')for a in allowed)for p in staged)
subprocess.run(['git','commit','-q','-m','Submit verified Q1464 T750911 square workspace result'],cwd=ws,check=True);print('Committed complete source, benchmark, independent evidence review and automatic upload receipt; unrelated edits remain unstaged.')
