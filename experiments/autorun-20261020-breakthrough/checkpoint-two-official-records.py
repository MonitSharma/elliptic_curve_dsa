from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
for folder,count,Q,T in[('breakthrough-context-lease-final-20261020',198,1480,750705),('breakthrough-native-both-final-20261020',200,1464,748691)]:
 p=root/'experiments'/folder;a=json.loads((p/'OFFICIAL-RESULT.json').read_text());v=json.loads((p/'PUBLIC-SOURCE-VERIFICATION.json').read_text());l=json.loads((p/'LOCAL-VERIFICATION.json').read_text());assert a['Q']==Q and a['T']==T and v['source_files']==count and v['protected_files']==17 and l['source_files']==count
stamp=datetime.now(timezone.utc);sgt=(stamp+timedelta(hours=8)).strftime('%d October %Y, %H:%M SGT')
prefix=f'''## Official Toffoli record · {sgt}

The challenge officially reproduced **1,464 qubits ×748,691 rounded mean
executed Toffolis =1,096,083,624**, all9,024 benchmark shots passing, in
[submission d182a53e](https://api.ecdsa.fail/api/submissions/d182a53e-be3d-4119-8298-303a9a9de07a).
This saves **2,014 Toffolis and16 qubits** versus the immediately preceding
official [Q1480/T750705 result](https://api.ecdsa.fail/api/submissions/260b3ba0-d604-4f0d-9d55-934055d216b4),
and2,220 Toffolis at unchanged width versus the earlier Q1464/T750911 result.
The fresh13:37UTC public snapshot confirms the independent T minimum.
Global product **933,497,554** remains lower; promotion was declined solely
because that global score did not improve. Both submissions use **GPT-6 sol / Codex**.

Exact native rail and G6 components from public stack-v3/88869 are ported onto
our strengthened comparison/public140 circuit, with fresh complete stream
bindings. No new approximate window, witness truncation or correctness cut is
adopted. Its own final2,097,152-shot-per-source gate passes; lowest nonce95,
128 screens and all controls are disclosed. All200 public source files and17
protected files match the locally verified source byte-for-byte as Git objects.

[Source and disclosures](experiments/breakthrough-native-both-final-20261020/SUBMISSION-NOTE.md) ·
[Local verification](experiments/breakthrough-native-both-final-20261020/LOCAL-VERIFICATION.json) ·
[Official source verification](experiments/breakthrough-native-both-final-20261020/PUBLIC-SOURCE-VERIFICATION.json)

'''
plan=f'''## {sgt}: two official T improvements; global product work continues

Official260b3ba0 reproduces Q1480/T750705/product1111043400, sourceaf60c815,
198/17 public bytes verified. Officiald182a53e then reproduces
Q1464/T748691/product1096083624, sourcefb2d03e8,200/17 bytes verified.
Both use GPT-6 sol/Codex and were submitted automatically immediately after
complete unchanged benchmark/local member review. Both promotions decline
solely because global product is lower. Public13:37UTC confirms T748691 minimum,
product933497554 atQ1234/T756481 (e3b5c51f/source88869), width671.

Latest native exact rail/G6 source9cb5de5f retains uniform+2 comparisons,
public140, square1408 and all17 protected bytes. All raw/output records bind
to the frozen research stream. Native27 controls include6,416,896 strip lanes
and phase faults;512x64 development compares all four fixedcases. Seven output
differences occur only on joint value-failing inputs, no new wrong-value IDs,
zero dirty. Sole final native-rail-g6-fixed-final-20261020-v1 declared
13:14:31.878149UTC,32768x64/source, compares exact official260b streamd1f5e785
against nonce0a871e42c: value1109/1109 identical IDs, phase593/589, dirty0/0,
failed1140/1131, candidate4.8666687/packet, b14/c23, p0.9505641, pairedT
-2010.919806 with SE0.3917466. PASS once, no rerun/relabel/extension.
Lowestnonce95,128 screens1..128, solepass95, overrun96..128, eight extra
partial controls repeated in production and24 full-state/RNG/curve controls.
Selected full9024 replay and unchanged benchmark pass; total6756188197.
Final streamcec71544, records251b3ebe, pre-tail40140a4d, archive18a589ae,
patch8130c7cb. All296 evidence members and200 source members verify locally.
All three direct dependencies (a4ee arithmetic,e3b exact components,260b gate
comparator) are disclosed. No global product or universal-correctness claim.

Earlier context213 source0fcd6ac4 has its own distinct final gate PASS,
nonce221/256 screens; all177 evidence and198 source members verify locally.
The fixed16384-operation proof context finds345 unconditional leases on olda4ee,
7 native controls, but is only a component result; do not count it as scored.

Global product remains the active unfinished goal. Newpublic714c full control
reproduces exactly. Raw witness28 stays measuredQ1234;1233/1232 stop the
unchangedy16 guard at forward128. Lean128 produces byte-identical positive
raw streams and the same lowerbudget failures (its path is ineligible there).
New original carry-loan128 restoration is predeclared/running: parentretuned
128..137 to129..137, losing one loan at the admission cliff. Preserve all
failures, no guard weakening. Next inspect actualQ and full-source correctness
if legal. A later read-only classical/AND carry-pebbling audit may reduce peak
without globally retuning every ladder. No packet-dependent circuit changes.

'''
handoff=f'''## {sgt}: official T748691; continue global product objective

Latest publicT: d182a53e, Q1464/T748691, sourcefb2d03e8; official metrics equal
complete local benchmark, all200 point-add and17 protected Git-object bytes
verified. Prior260b Q1480/T750705/sourceaf60c815 also reproduced198/17. Auto-
submit every newly verified current-record improvement as GPT-6 sol/Codex.
Never ask again for publication approval. Full evidence under the corresponding
breakthrough-native-both-final and breakthrough-context-lease-final directories.
Global product933497554 (e3b5c51f, Q1234/T756481/source88869) is still lower;
active product goal is NOT complete. PreserveQ692, failedProduct25/Product84,
all other final failed verdicts, preexisting root edits and unrelated jobs.

Nativeboth source9cb5de5f, nonce95,128 production screens,27 native controls,
one final32768x64 gate PASS(p0.950564), every source/evidence byte verified.
Exact primary components credited to public88869; no new approximation adopted.
Current product probe: breakthrough-stackv3-width-loan128-20261020, supervisor
2853827. Restore original exact forward128 carry loan to remove a one-wire
admission cliff; first reproduce714c full public control, then fixed rawcap
1234/1233/1232 with21-control/28-stronger witness. All old guards unchanged.
Earlier lean128 no-effect and rawlowerbudget failures remain. Do not treat
nominalcap or staticproxy as scoredQ/T. Inspect output/hashes and native contracts
before any own final gate, qualified ascending nonce, unchanged benchmark and
auto-submission. Classical-at-peak or isolated carry measure/recompute may be a
next exact width route; no such probe/result is implemented yet.

'''
docprefixes={'README.md':prefix,'docs/research-plan.md':plan,'docs/AGENT_HANDOFF.md':handoff}
for path,addition in docprefixes.items():
 p=root/path;work=p.read_bytes();base=git('show','HEAD:'+path);data=addition.encode();assert not work.startswith(data);p.write_bytes(data+work);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
state={'at_utc':stamp.isoformat(),'last_root_commit':'7f1b6303','submission_mode':'auto','official_T':{'id':'d182a53e-be3d-4119-8298-303a9a9de07a','Q':1464,'T':748691,'product':1096083624,'public_source':'fb2d03e8a70a8b69965710ef46c5cdce828e9ca2','local_source':'9cb5de5f5431062c927bd993564ed3c2a2502884','source_files':200,'protected_files':17,'local_verified_evidence_members':296,'nonce':95,'screens':128},'previous_official_T':{'id':'260b3ba0-d604-4f0d-9d55-934055d216b4','Q':1480,'T':750705,'source':'af60c815cf7fcb927466450864cd30b03483c74c','source_files':198,'protected_files':17,'evidence_members':177,'nonce':221,'screens':256},'current_global_product':{'id':'e3b5c51f-74e6-480a-82bf-5543fb1ba555','Q':1234,'T':756481,'product':933497554,'source':'88869d8cc23fb72120dd52533f3e48277e9b36e4'},'goal':'Active global product objective unfinished. Keep working; do not mark complete or end at checkpoint. Auto-submit each newly complete verified current-record improvement after fresh exact parent gate, ascending lowest nonce, unchanged benchmark and local source/evidence review.','active_job':{'directory':'breakthrough-stackv3-width-loan128-20261020','pid':2853827,'scope':'Restore prior exact carryloan128, fixedfull714c control then rawwidth grid21/28 precision. No gate/nonce/benchmark.','status':'Await first full control then raw cases.','if_fits':'Measure actualQ using protected stats utility; finish self-contained native+generic exact pipeline and validate freshfulloutput/census before any final gate/nonce.'},'completed_to_preserve':['context16384 proof345leases7controls, componentonly','exact-native-ports-v3 all4fixedcases27controls, native6416896lanes, originalrun.exit1 environmentfailure retained; resumed.exit0','exact-ports-development512batches,7jointfailure targetdifferences only, no new valuefail/otherancilladifferences','native-both-finished200/17, full raw+generic equality guards','stackv3-width714c control exact,raw1234/t21and28;lowerbudget1233/1232 y16fwd128 constructionstops','stackv3-width-lean128 no-effect rawpositive bytesidenticaland samefailures','stackv3-width-stats actualQ1234allcompletedstreams,staticcountsnotexecuted'], 'next_research':'After current exact carryloan probe, consider read-only audit of classical-at-peak or isolated carry measure/recompute. Potential zero-T classical clear/restore or one-T carry pebble with interval remapping; not implemented/proved, no result claimed. Preserve fixedsource/final failedgates and no packet-dependent content.'}
(r/'CURRENT-1020-1340.json').write_text(json.dumps(state,indent=2)+'\n')
folders=['breakthrough-context-lease-final-20261020','breakthrough-native-both-finished-20261020','breakthrough-native-both-final-gate-20261020','breakthrough-native-both-nonce-20261020','breakthrough-native-both-final-20261020','breakthrough-stackv3-width-lean128-20261020','breakthrough-stackv3-width-loan128-20261020','breakthrough-stackv3-width-stats-20261020']
scripts=['prepare-native-both-finished.py','prepare-native-both-controllers.py','native-both-sealer-tail.py','prepare-native-both-packaging.py','collect-native-both-final.py','prepare-context-official-checks.py','prepare-native-both-official-checks.py','prepare-stack-lean128.py','prepare-stack-loan128.py','prepare-width-stats.py','checkpoint-two-official-records.py','CURRENT-1020-1340.json']
paths=['experiments/'+n for n in folders]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]
for n in['.gitattributes','leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz','SNAPSHOT-MANIFEST.json']:paths.append('experiments/breakthrough-assessment-20261020/snapshots/20261020T133748Z/'+n)
subprocess.run(['git','-C',str(root),'add','--']+paths,check=True);allowed=paths+list(docprefixes);staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q.rstrip('/')+'/')for q in allowed)for p in staged);assert all('resource-preflight'not in p for p in staged);subprocess.run(['git','-C',str(root),'commit','-q','-m','Publish two officially reproduced T records and preserve active exact width research'],check=True);print('Official T748691 and T750705 evidence/disclosures saved; only owned additive documentation staged. Product goal remains active.')
