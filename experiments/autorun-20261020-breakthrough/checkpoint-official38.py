import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
official=json.loads((root/'experiments/breakthrough-native-context-final-20261020/OFFICIAL-RESULT.json').read_text());verified=json.loads((root/'experiments/breakthrough-native-context-final-20261020/LOCAL-VERIFICATION.json').read_text());gate=json.loads((root/'experiments/breakthrough-groups-safe-final-gate-20261020/GATE-RESULT.json').read_text())
assert official['T']==748184 and verified['members']==240 and gate['verdict']=='FAILURE_RATE_GATE_PASS'
state={'at_utc':datetime.now(timezone.utc).isoformat(),'objective':'Global complete product improvement remains active; automatically submit each complete verified current-record improvement as GPT-6 sol/Codex.','official_latest':official,'local_evidence':verified,'latest_public_snapshot':'experiments/breakthrough-assessment-20261020/snapshots/20261020T155716Z','public_product':{'id':'acd0d88e-7445-4430-ba59-3c24c9bf4e0f','Q':1234,'T':756265,'product':933231010,'source':'7499c902d7989e5a995ccd2331104a532197851b'},'public_width':{'Q':670,'id':'e2e13cf3-6711-4a39-8a24-b3ddda56f56c'},'groups_safe_final_gate':gate,'active_jobs':[{'directory':'breakthrough-groups-safe-nonce-20261020','pid':2941100,'purpose':'Qualified ascending nonce1..65536 windows64 after own gatePASS; lowest pass; never select by cost.'},{'directory':'breakthrough-groups-safe-final-20261020','pid':2941227,'purpose':'Waitnonce, unchangedbenchmark;204source/17protected, onlynonce literal change.'},{'directory':'breakthrough-groups-safe-final-20261020','pid':2942531,'purpose':'Waitbenchmark, seal source/evidence and honestdisclosures; then collect/localverify before guarded automatic upload.'}],'next_product_front':'Lowcap1234/1233 stronger grouped square stops original y16 m0erase guard one helper short. Investigate exact terminal phase carry expansion to save one comparator helper; native proof/phase/width/fault controls mandatory. No implementation or result yet.','superseded_product_family':'Publice3 cache53/live7 development complete, no newvalues/dirty; finalgate preflight stopped because acd0 public record changed. No gate declaration, census or verdict exists. Do not rerun against old record.','preservation':'Original assemblyv1/v2 failed before freeze; prototype missingtestenv failure and resumed0; caps localparser original kept. Need seal remaining completed fronts and partial source snapshots. Preserve all user root/submodule edits and unrelated server jobs.'}
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026, 00:21 SGT: officialT748184; grouped square gate PASS

Automatic submission38a686dd officially reproduces Q1480/T748184/product1107312320,
507 fewerT than d182 at16 extraQ. Public sourcee3d3f05e; all201source/17protected
Git object bytes match localf934c592. All240 evidence and201source archive members
verified locally. Promotion rejected solely because global product is lower.
Globalproduct933231010 atQ1234/T756265 (acd0/source7499), width670 as fresh15:57UTC.
Globalproduct goal remains active; auto-submit each complete verified improvement.

New grouped-square candidate retains stronger28bit/full259tail/exact capped splits,
depth8 inverseleaf and uniform+2/public140/native rail/G6. MeasuredQ1464,204source,
17protected; complete raw/output records bound, no old index transport. Own2native
plus27 inherited controls; prototype contract has six disclosed historical edge
exclusions, junction fault detected.512x64 full-output dev has no target/otherlane
differences or newvalues/dirty. Sole finalgroups-safe28-full259-final-20261020-v1
32768x64/source PASS: value1227parent/1216candidate (6newbad,17newpass), phase646/667,
dirty0/0,failed1273/1255,b15/c33,p.9972424,5.400238failedbatches/packet.
DiagnosticpairedT-739.2920,SE.320833; not scored. Sourcefreeze13d25aa0,nonce0dc1478c1.
Qualifiednonce2941100,benchmark2941227,review2942531 running; source/evidence
must be collected and every member locally verified before freshrecordguarded upload.
No new final score yet. Read CURRENT-ACTIVE.json and actual stage logs.

Olde3 cache53/live7 gate stopped before declaration when acd0 changed record;
no census/verdict/nonce. Lowercap grouped circuit1234/1233 fails unchangedm0erase
onehelper short, no pointstream/score. Next exact comparator space-saving probe.
Never rerun/relabel a declared finalgate; preserve all original failures and
userchanges. Missingtestenv prototype failure corrected before arithmetic;
assemblyv1/v2 failedbeforeSF. No chemistry changes; unrelatedQOB jobs untouched.

'''
readme='''## Official Toffoli improvement · 21 October 2026, 00:21 SGT

The challenge officially reproduced **1,480 qubits × 748,184 rounded mean
executed Toffolis = 1,107,312,320**, all9,024 shots passing, in
[submission38a686dd](https://api.ecdsa.fail/api/submissions/38a686dd-a2b1-4bdc-899e-81a389d36fd5).
This saves **507 Toffolis** versus the preceding officialT748691 result,
using16 additional qubits. The fresh15:57UTC snapshot confirms the independent
Toffoli minimum. The global product933,231,010 remains lower; promotion was
declined solely because that score did not improve. Attribution **GPT-6 sol / Codex**.

The new499 exact context-product leases have their own passed final statistical
gate, disclosed lowestnonce9/64screens and complete unchanged benchmark. Every
source/protected byte matches the official commit. These are complete official
measurements; ongoing research candidates are documented separately.

[Source and disclosures](experiments/breakthrough-native-context-final-20261020/SUBMISSION-NOTE.md) ·
[Local evidence verification](experiments/breakthrough-native-context-final-20261020/LOCAL-VERIFICATION.json) ·
[Official source verification](experiments/breakthrough-native-context-final-20261020/PUBLIC-SOURCE-VERIFICATION.json)

'''
for path,prefix in [('README.md',readme),('docs/AGENT_HANDOFF.md',addition),('docs/research-plan.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());base=git('show','HEAD:'+path);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=['breakthrough-native-context-final-20261020','breakthrough-native-context-finished-20261020','breakthrough-native-context-finished-v2-20261020','breakthrough-native-context-finished-v3-20261020','breakthrough-native-context-development-20261020','breakthrough-native-context-final-gate-20261020','breakthrough-native-context-nonce-20261020','breakthrough-grouped-square-ports-20261020','breakthrough-grouped-square-caps-20261020','breakthrough-groups-safe-finished-20261020','breakthrough-groups-safe-development-20261020','breakthrough-groups-safe-final-gate-20261020','breakthrough-groups-safe-nonce-20261020','breakthrough-groups-safe-final-20261020']
scripts=[p.relative_to(root).as_posix() for p in a.glob('*.py') if p.name.startswith(('prepare-native-context-','collect-native-context-','prepare-grouped-square-','prepare-groups-safe-','collect-groups-safe-','checkpoint-official38'))]
paths=['experiments/'+n for n in dirs]+scripts+['experiments/autorun-20261020-breakthrough/CURRENT-ACTIVE.json','experiments/breakthrough-native-both-context16-20261020/SCOPE-CORRECTION.json','experiments/breakthrough-assessment-20261020/snapshots/20261020T151114Z','experiments/breakthrough-assessment-20261020/snapshots/20261020T155716Z']
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md'];assert all(any(p==q or p.startswith(q+'/') for q in allowed) for p in staged);assert not any('resource-preflight' in p or '/candidate/' in p or '/tool/' in p or p.endswith('ops.bin') for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve official T748184 source and evidence; grouped-square final gate passes'],check=True);print(git('rev-parse','HEAD').decode().strip())
